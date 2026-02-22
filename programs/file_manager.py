class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"📂 Opening file: {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"🔒 Closing file: {self.filename}")
        if self.file:
            self.file.close()
        
        if exc_type:
            print(f"❌ Error occurred: {exc_value}")
        return False  # Don't suppress exceptions

# Usage:
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")
    f.write("This is a test.")

# Output:
# 📂 Opening file: test.txt
# 🔒 Closing file: test.txt