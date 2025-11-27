/**
 * File Upload Handler
 * IMPORTANT ISSUE: Missing error handling
 */

class FileUploadHandler {
  constructor(uploadPath) {
    this.uploadPath = uploadPath;
    this.maxFileSize = 10 * 1024 * 1024; // 10MB
  }

  // IMPORTANT: No error handling for file operations
  async uploadFile(file) {
    const filename = `${Date.now()}-${file.name}`;
    const filepath = `${this.uploadPath}/${filename}`;

    // Missing try-catch, no validation of file.data
    await fs.writeFile(filepath, file.data);

    return { filename, filepath, size: file.data.length };
  }

  // IMPORTANT: Unhandled promise rejection
  async processUpload(fileBuffer) {
    const metadata = await this.extractMetadata(fileBuffer);
    // extractMetadata can throw, but no error handling
    return this.saveToDatabase(metadata);
  }
}

module.exports = FileUploadHandler;
