import json
from pathlib import Path

def merge_logs(user_id, output_file="merged_logs.json"):
    log_dir = Path("logs") / user_id
    merged = []

    for log_file in log_dir.glob("*.json"):
        if log_file.name == output_file:
            continue  # avoid including the output file if it already exists
        try:
            with open(log_file, encoding='utf-8') as f:
                data = json.load(f)
            merged.append(data)
        except Exception as e:
            print(f"Error reading {log_file.name}: {e}")

    output_path = log_dir / output_file
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"Merged {len(merged)} logs into {output_path}")

# Örnek kullanım:
if __name__ == "__main__":
    merge_logs(user_id="kullanici_adi")  # Buraya kullanıcı ID'sini yaz
