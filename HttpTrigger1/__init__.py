import logging
import azure.functions as func
import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
import io
from azure.storage.blob import BlobServiceClient

def create_model():
    model = Sequential()
    try:
        # Define your model architecture here
        # Make sure to define the same architecture as the one used during training
        model.add(Conv2D(32, (5, 5), activation='relu', input_shape=(224, 224, 3), kernel_initializer='he_normal'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))

        model.add(Conv2D(64, (5, 5), activation='relu', kernel_initializer='he_normal'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))

        model.add(Conv2D(128, (5, 5), activation='relu', kernel_initializer='he_normal'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))

        model.add(Flatten())

        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.6))

        model.add(Dense(1, activation='sigmoid'))

        model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])
        return model
    except Exception as e:
        logging.error(f"An error occurred while creating the model: {str(e)}")
        return None

def load_environment_variables_from_keyvault():
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        # Authenticate to your Azure Key Vault using DefaultAzureCredential
        credential = DefaultAzureCredential()

        # Replace 'your-key-vault-url' with the URL of your Azure Key Vault
        keyvault_url = "https://kerastbkeys.vault.azure.net/"
        secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

        # Retrieve secrets from Azure Key Vault
        azure_storage_connection_string = secret_client.get_secret("ConnectionString").value
        container_name = secret_client.get_secret("Container").value
        blob_name = secret_client.get_secret("BlobURL").value

        return azure_storage_connection_string, container_name, blob_name
    except Exception as e:
        logging.error(f"An error occurred while loading environment variables from Key Vault: {str(e)}")
        return None




def load_model_weights_from_blob(container_name, blob_name):
    try:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        # Authenticate to your Azure Key Vault using DefaultAzureCredential
        credential = DefaultAzureCredential()

        # Replace 'your-key-vault-url' with the URL of your Azure Key Vault
        keyvault_url = "https://kerastbkeys.vault.azure.net/"
        secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

        # Retrieve secrets from Azure Key Vault
        blob_url = secret_client.get_secret("BlobURL").value
        sas_token = secret_client.get_secret("SAS").value

        # Construct the Blob URL with SAS token
        blob_url_with_sas = f"{blob_url}{sas_token}"

        # Create BlobServiceClient using the constructed Blob URL with SAS token
        blob_service_client = BlobServiceClient(account_url=blob_url_with_sas)

        # Get the Blob Client for the specified container and blob name
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Check if 'imageFile' exists in the request
        if 'imageFile' in req.files:
            image_file = req.files['imageFile'][0]

            # Upload the file to the Blob Storage container
            with open(image_file.filename, "rb") as data:
                blob_client.upload_blob(data)

            return func.HttpResponse("File uploaded successfully.")
        else:
            return func.HttpResponse("No file found in the request.", status_code=400)

    except Exception as e:
        logging.error(f"Error during image processing: {str(e)}")
        return func.HttpResponse("An error occurred during image processing.", status_code=500)



@func.blob_trigger(name="BlobTriggerFunction", path="azure-webjobs-hosts/{name}.{ext}", connection="AzureWebJobsStorage")
def load_and_preprocess_image(uploaded_image, target_size=(224, 224)):
    try:
        # Open the image using PIL
        image = Image.open(uploaded_image)

        # Resize the image to the target size while preserving aspect ratio
        image = image.resize(target_size, Image.ANTIALIAS)

        # Convert the image to a NumPy array
        image_array = np.asarray(image)

        # Normalize the pixel values to the range [0, 1]
        image_array = image_array / 255.0

        # Expand the dimensions to match expected model input shape
        # (Assuming a model expecting a single-channel image)
        preprocessed_image = np.expand_dims(image_array, axis=0)

        return preprocessed_image

    except Exception as e:
        logging.error(f"Error during image preprocessing: {e}")
        return None


def main(req: func.HttpRequest, myblob: func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        try:
            # Preprocess the uploaded image
            preprocessed_image = load_and_preprocess_image(myblob)

            if preprocessed_image is not None:
                # Load model weights from Azure Blob Storage using secrets from Key Vault
                connection_string, container_name, blob_name = load_environment_variables_from_keyvault()
                model = load_model_weights_from_blob(container_name, blob_name)

                # Perform inference
                if model is not None:
                    prediction = model.predict(preprocessed_image)
                    prediction_class = 'TB' if prediction > 0.5 else 'No TB'
                    return func.HttpResponse(f"Hello, {name}. Prediction: {prediction_class}")
                else:
                    return func.HttpResponse(
                        "Failed to load model from Blob Storage.",
                        status_code=500
                    )
            else:
                return func.HttpResponse(
                    "An error occurred during image preprocessing.",
                    status_code=500
                )

        except Exception as e:
            logging.error(f"Error during image classification: {e}")
            return func.HttpResponse(
                "An error occurred during image processing.",
                status_code=500
            )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )