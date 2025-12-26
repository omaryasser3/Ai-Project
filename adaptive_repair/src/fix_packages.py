import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "java_programs")
PACKAGE_DECL = "package java_programs;\n"

def fix_packages():
    count = 0
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".java"):
            continue
            
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            if content.strip().startswith("package java_programs;"):
                print(f"Skipping {filename} (already has package)")
                continue
                
            new_content = PACKAGE_DECL + "\n" + content
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print(f"Fixed {filename}")
            count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    print(f"\nTotal files fixed: {count}")

if __name__ == "__main__":
    if os.path.exists(DATA_DIR):
        fix_packages()
    else:
        print(f"Directory not found: {DATA_DIR}")
