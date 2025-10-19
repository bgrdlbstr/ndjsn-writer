import os
import json
import random
import string
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Output directory for generated files
OUTPUT_DIR = "data_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def random_string(length=10):
    """Generate a random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_sub_dictionary():
    """Generate a dictionary with 10-30 fields of mixed types"""
    num_fields = random.randint(10, 30)
    sub_dict = {}

    for i in range(1, num_fields + 1):
        field_name = f"field{i:03d}"

        # Assign consistent types to specific field ranges
        if i <= 10:
            # First 10 fields are integers
            sub_dict[field_name] = random.randint(0, 10000)
        elif i <= 20:
            # Next 10 fields are floats
            sub_dict[field_name] = round(random.uniform(0, 1000), 2)
        else:
            # Remaining fields are strings
            sub_dict[field_name] = random_string(random.randint(5, 15))

    return sub_dict


def generate_ndjson_record():
    """Generate a single NDJSON record with 30 data points"""
    record = {}

    # mainDataPoint001-005: Integers
    for i in range(1, 6):
        record[f"mainDataPoint{i:03d}"] = random.randint(0, 100000)

    # mainDataPoint006-010: Floats
    for i in range(6, 11):
        record[f"mainDataPoint{i:03d}"] = round(random.uniform(0, 10000), 2)

    # mainDataPoint011-015: Strings
    for i in range(11, 16):
        record[f"mainDataPoint{i:03d}"] = random_string(random.randint(8, 20))

    # mainDataPoint016-020: Integers
    for i in range(16, 21):
        record[f"mainDataPoint{i:03d}"] = random.randint(-1000, 1000)

    # mainDataPoint021-024: Floats
    for i in range(21, 25):
        record[f"mainDataPoint{i:03d}"] = round(random.uniform(-100, 100), 3)

    # mainDataPoint025-028: Strings
    for i in range(25, 29):
        record[f"mainDataPoint{i:03d}"] = random_string(random.randint(5, 12))

    # mainDataPoint029: Integer
    record["mainDataPoint029"] = random.randint(1, 1000)

    # mainDataPoint030: Array of dictionaries (2-5 dictionaries)
    num_dicts = random.randint(2, 5)
    record["mainDataPoint030"] = [generate_sub_dictionary() for _ in range(num_dicts)]

    return record


def generate_ndjson_file(num_records, file_prefix):
    """Generate an NDJSON file with specified number of records"""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"
    filename = f"{file_prefix}_{num_records}_{timestamp}.ndjson"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Use buffered writing with list comprehension for efficiency
    with open(filepath, 'w', buffering=8192 * 16) as f:
        # Generate all records and write in batches
        batch_size = 1000
        for batch_start in range(0, num_records, batch_size):
            batch_end = min(batch_start + batch_size, num_records)
            batch = [json.dumps(generate_ndjson_record()) for _ in range(batch_end - batch_start)]
            f.write('\n'.join(batch) + '\n')

    return filename, num_records


@app.get("/smallData")
async def generate_small_data():
    """Generate NDJSON file with 1-100 records"""
    num_records = random.randint(1, 100)
    filename, count = generate_ndjson_file(num_records, "small_data")

    return JSONResponse(
        content={
            "status": "success",
            "filename": filename,
            "records_generated": count,
            "file_path": os.path.join(OUTPUT_DIR, filename),
            "type": "small_data"
        }
    )


@app.get("/bigData")
async def generate_big_data():
    """Generate NDJSON file with 500-10000 records"""
    num_records = random.randint(500, 10000)
    filename, count = generate_ndjson_file(num_records, "big_data")

    return JSONResponse(
        content={
            "status": "success",
            "filename": filename,
            "records_generated": count,
            "file_path": os.path.join(OUTPUT_DIR, filename),
            "type": "big_data"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NDJSON Data Generator API",
        "endpoints": {
            "/smallData": "Generate 1-100 NDJSON records",
            "/bigData": "Generate 500-10,000 NDJSON records"
        },
        "output_directory": OUTPUT_DIR,
        "data_structure": {
            "mainDataPoint001-005": "integer",
            "mainDataPoint006-010": "float",
            "mainDataPoint011-015": "string",
            "mainDataPoint016-020": "integer",
            "mainDataPoint021-024": "float",
            "mainDataPoint025-028": "string",
            "mainDataPoint029": "integer",
            "mainDataPoint030": "array of dictionaries (10-30 fields each)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)