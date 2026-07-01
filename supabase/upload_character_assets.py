import os
import json
from supabase import create_client, Client
from pathlib import Path

# Load environment variables (Supabase URL and Key)
# It's crucial to set these securely. For local development, a .env file is common.
# In production, use your deployment platform's secrets management.
# Example:
# SUPABASE_URL="YOUR_SUPABASE_URL"
# SUPABASE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY" # Use service role key for write access
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase URL and Key must be set as environment variables "
        "(SUPABASE_URL, SUPABASE_KEY). "
        "Please ensure you are using a service role key with write access."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuration ---
STORAGE_BUCKET_NAME = "character-base"
MANIFEST_FILE = Path("home_vocab/character_base_manifest.json")
METHOD_DOC_PATH = "CHARACTER_ASSET_METHOD.md" # Relative path to the method document

# --- Helper Functions ---

def upload_image_to_storage(file_path: Path, bucket_name: str):
    """Uploads an image to Supabase Storage and returns its public URL."""
    with open(file_path, "rb") as f:
        file_name = file_path.name
        try:
            # Upload file
            response = supabase.storage.from_(bucket_name).upload(file_name, f)
            print(f"Uploaded {file_name} to bucket {bucket_name}.")
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
            return public_url
        except Exception as e:
            # If the file already exists, we might want to update it or skip.
            # Supabase storage upload raises an error if file exists by default.
            # To overwrite, you'd typically delete first or use an upsert-like functionality
            # if provided by the client library or a custom API.
            # For simplicity, we'll try to get the public URL if upload fails (assuming it exists).
            print(f"Error uploading {file_name}: {e}")
            print(f"Attempting to get public URL for existing file: {file_name}")
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
            if public_url:
                print(f"Found existing public URL for {file_name}: {public_url}")
                return public_url
            else:
                raise # Re-raise if we can't even get public URL

def create_storage_bucket_if_not_exists(bucket_name: str):
    """Creates a Supabase Storage bucket if it doesn't already exist."""
    try:
        supabase.storage.create_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        if "Bucket already exists" in str(e):
            print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
        else:
            raise Exception(f"Failed to create bucket '{bucket_name}': {e}")

def ensure_table_exists(table_name: str, schema_definition: dict):
    """
    Ensures a table exists with the specified schema.
    NOTE: This is a very basic implementation and does not handle migrations or complex types.
          It assumes the table either doesn't exist or has a compatible schema.
          For production, use Supabase migrations.
    """
    try:
        # Attempt to fetch table info to check existence
        # This approach is not ideal as Supabase client doesn't expose table creation directly
        # A better approach would be to use SQL via rpc or a separate migration system.
        # For this task, we will assume table 'character_assets' and 'characters' might need to be created.
        # We will create a simple SQL DDL for initial table creation if it fails to insert.
        print(f"Checking for table '{table_name}'...")
        response = supabase.from_(table_name).select('*').limit(1).execute()
        print(f"Table '{table_name}' exists.")
        return True
    except Exception as e:
        print(f"Table '{table_name}' might not exist or there was an error accessing it: {e}")
        return False

def create_character_assets_table_sql():
    """Returns SQL to create the character_assets table."""
    return """
    CREATE TABLE IF NOT EXISTS character_assets (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        character_id TEXT NOT NULL,
        character_name_kr TEXT,
        character_name_en TEXT,
        character_gender TEXT,
        asset_key TEXT NOT NULL,
        view TEXT NOT NULL,
        pose TEXT DEFAULT 'standing',
        file_path TEXT NOT NULL,
        storage_url TEXT NOT NULL,
        method TEXT,
        style TEXT,
        tags TEXT[],
        method_doc_path TEXT,
        identity TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_character_id_view ON character_assets (character_id, view);
    """

def create_characters_table_sql():
    """Returns SQL to create the characters table."""
    return """
    CREATE TABLE IF NOT EXISTS characters (
        id TEXT PRIMARY KEY,
        name_kr TEXT,
        name_en TEXT,
        gender TEXT,
        identity TEXT,
        style TEXT,
        tags TEXT[]
    );
    """

def run_sql_command(sql: str):
    """Executes a raw SQL command using Supabase RPC (if available) or by hinting the user."""
    print(f"Attempting to run SQL command:\n{sql}")
    try:
        # Supabase Python client doesn't have a direct 'execute_sql'
        # We can try to use RPC to call a dummy function or instruct the user.
        # For simplicity, we will assume the user has run the migrations or will do so manually.
        # This part requires manual intervention or a more robust system.
        # As a workaround, we'll tell the user to execute it if needed.
        print("Note: Direct SQL execution via Supabase Python client is limited.")
        print("Please ensure the tables 'characters' and 'character_assets' are created in your Supabase project.")
        print("You can use the following SQL to create them if they don't exist:")
        print(create_characters_table_sql())
        print(create_character_assets_table_sql())
    except Exception as e:
        print(f"Error running SQL command (might require manual execution): {e}")


# --- Main Logic ---
def main():
    print("Starting character asset upload to Supabase...")

    # 1. Ensure storage bucket exists
    create_storage_bucket_if_not_exists(STORAGE_BUCKET_NAME)

    # 2. Ensure tables exist (or instruct user to create)
    run_sql_command("") # Placeholder to inform user about table creation

    # Load manifest data
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    all_uploaded_urls = []
    all_inserted_records = []

    # Process characters and their base photos
    for character in manifest_data["characters"]:
        character_id = character["id"]
        character_name_kr = character.get("name_kr")
        character_name_en = character.get("name_en")
        character_gender = character.get("gender")
        identity = character.get("identity")
        style = character.get("style")
        char_tags = manifest_data.get("tags", []) + [character_id] # Add character_id to tags

        # Insert/Update characters table
        try:
            # Check if character already exists
            existing_char = supabase.from_('characters').select('id').eq('id', character_id).execute()
            if not existing_char.data:
                supabase.from_('characters').insert({
                    'id': character_id,
                    'name_kr': character_name_kr,
                    'name_en': character_name_en,
                    'gender': character_gender,
                    'identity': identity,
                    'style': style,
                    'tags': char_tags
                }).execute()
                print(f"Inserted character '{character_id}' into 'characters' table.")
            else:
                print(f"Character '{character_id}' already exists in 'characters' table. Skipping insertion.")
        except Exception as e:
            print(f"Error inserting/checking character '{character_id}': {e}")


        for photo in character["base_photos"]:
            file_path = Path(photo["file"])
            if not file_path.exists():
                print(f"Warning: Image file not found: {file_path}. Skipping.")
                continue

            print(f"Processing image: {file_path}")
            storage_url = upload_image_to_storage(file_path, STORAGE_BUCKET_NAME)
            all_uploaded_urls.append(storage_url)

            # Prepare data for 'character_assets' table
            record = {
                "character_id": character_id,
                "character_name_kr": character_name_kr,
                "character_name_en": character_name_en,
                "character_gender": character_gender,
                "asset_key": photo["key"],
                "view": photo["view"],
                "pose": photo.get("pose", "standing"), # Default to 'standing' if not specified
                "file_path": str(file_path),
                "storage_url": storage_url,
                "method": photo.get("method"),
                "style": style, # Inherit from character
                "tags": char_tags, # Inherit from manifest and character
                "method_doc_path": METHOD_DOC_PATH,
                "identity": identity # Inherit from character
            }

            try:
                # Check if asset already exists using character_id and asset_key
                existing_asset = supabase.from_('character_assets').select('id').eq('character_id', character_id).eq('asset_key', photo["key"]).execute()
                if not existing_asset.data:
                    supabase.from_('character_assets').insert(record).execute()
                    all_inserted_records.append(record)
                    print(f"Inserted record for {photo['key']} into 'character_assets'.")
                else:
                    print(f"Record for {photo['key']} already exists in 'character_assets'. Skipping insertion.")
            except Exception as e:
                print(f"Error inserting record for {photo['key']}: {e}")

    print("\n--- Summary ---")
    print(f"Uploaded {len(all_uploaded_urls)} images to bucket '{STORAGE_BUCKET_NAME}'.")
    print(f"Inserted {len(all_inserted_records)} new records into 'character_assets' table.")
    print("\nAll uploaded image URLs:")
    for url in all_uploaded_urls:
        print(url)
    print("\nPlease ensure your Supabase tables 'characters' and 'character_assets' are properly set up (if not already).")

if __name__ == "__main__":
    main()