/**
 * Goings OS Executive Control Plane v4.2
 * Script: MCP Archival Task for Luxury Decor & Rentals LLC
 * Ingests formation PDFs, creates target Drive folder, uploads via MCP with SHA-256,
 * and records Drive file IDs in data/goings_os_vault.db.
 * Compliance: Zero em-dashes; zero double-hyphens.
 */

import * as fs from "node:fs"
import * as path from "node:path"
import * as crypto from "node:crypto"
import { DatabaseSync } from "node:sqlite"

import {
  mcpDriveCreateFolder,
  mcpDriveUploadFile,
  type DriveFolderResult,
  type DriveUploadResult,
} from "../vite-monorepo/apps/web/src/lib/workspace.ts"

// Target Entity & Drive Folder
const ENTITY_NAME = "Luxury Decor & Rentals LLC"
const TARGET_DRIVE_FOLDER = "Master Architecture/Entities/Luxury Decor & Rentals LLC"
const VAULT_DB_PATH = path.resolve("data", "goings_os_vault.db")
const ENTITY_DIR = path.resolve("data", "entities", "luxury_decor_rentals")

interface FormationDocMeta {
  documentType: "CERTIFICATE_OF_ORGANIZATION" | "ARTICLES_OF_ORGANIZATION" | "EIN_CONFIRMATION"
  fileName: string
}

const FORMATION_DOCS: FormationDocMeta[] = [
  {
    documentType: "CERTIFICATE_OF_ORGANIZATION",
    fileName: "Certificate_of_Organization.pdf",
  },
  {
    documentType: "ARTICLES_OF_ORGANIZATION",
    fileName: "Articles_of_Organization.pdf",
  },
  {
    documentType: "EIN_CONFIRMATION",
    fileName: "EIN_Confirmation_CP575.pdf",
  },
]

export interface ArchivalReportItem {
  documentType: string
  fileName: string
  filePath: string
  sha256Checksum: string
  driveFolderId: string
  driveFileId: string
  driveFileUrl: string
  dbRecordId: number | bigint
}

export async function executeLuxuryDecorArchival(): Promise<{
  folderResult: DriveFolderResult
  archivedFiles: ArchivalReportItem[]
}> {
  console.log("====================================================================")
  console.log("GOINGS OS // MCP ARCHIVAL TASK: LUXURY DECOR & RENTALS LLC")
  console.log("====================================================================")

  // Step 1: Verify ingestion of all 3 formation PDFs
  console.log("\n[STEP 1] Ingesting formation PDFs from:", ENTITY_DIR)
  for (const doc of FORMATION_DOCS) {
    const fullPath = path.join(ENTITY_DIR, doc.fileName)
    if (!fs.existsSync(fullPath)) {
      throw new Error(`Required formation document missing: ${fullPath}`)
    }
    const stats = fs.statSync(fullPath)
    console.log(`  - Ingested: ${doc.fileName} (${stats.size} bytes)`)
  }

  // Step 2: Create target folder in Google Drive via mcpDriveCreateFolder
  console.log("\n[STEP 2] Creating target Google Drive folder via mcpDriveCreateFolder:")
  console.log("  - Target Path:", TARGET_DRIVE_FOLDER)
  const folderResult: DriveFolderResult = await mcpDriveCreateFolder(TARGET_DRIVE_FOLDER)
  console.log("  - Folder ID:", folderResult.folderId)
  console.log("  - Folder URL:", folderResult.driveUrl)

  // Step 3: Upload and index all three files with SHA-256 checksums using mcpDriveUploadFile
  console.log("\n[STEP 3] Uploading and indexing formation documents via mcpDriveUploadFile:")
  const uploadResults: Array<{ meta: FormationDocMeta; upload: DriveUploadResult; fullPath: string }> = []

  for (const doc of FORMATION_DOCS) {
    const fullPath = path.join(ENTITY_DIR, doc.fileName)
    const fileBytes = fs.readFileSync(fullPath)
    const sha256Checksum = crypto.createHash("sha256").update(fileBytes).digest("hex")

    console.log(`  - Processing: ${doc.fileName}`)
    console.log(`    SHA-256: ${sha256Checksum}`)

    const uploadRes: DriveUploadResult = await mcpDriveUploadFile({
      folderPath: TARGET_DRIVE_FOLDER,
      folderId: folderResult.folderId,
      fileName: doc.fileName,
      mimeType: "application/pdf",
      fileBytes,
      sha256Checksum,
    })

    console.log(`    Drive File ID: ${uploadRes.fileId}`)
    console.log(`    Drive URL: ${uploadRes.driveUrl}`)
    uploadResults.push({ meta: doc, upload: uploadRes, fullPath })
  }

  // Step 4: Record resulting Google Drive file IDs in data/goings_os_vault.db
  console.log("\n[STEP 4] Recording archival records into data/goings_os_vault.db:")
  const db = new DatabaseSync(VAULT_DB_PATH)

  db.exec(`
    CREATE TABLE IF NOT EXISTS entity_document_archive (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_name TEXT NOT NULL,
      document_type TEXT NOT NULL,
      file_name TEXT NOT NULL,
      file_path TEXT NOT NULL,
      sha256_checksum TEXT NOT NULL,
      drive_folder_path TEXT NOT NULL,
      drive_folder_id TEXT NOT NULL,
      drive_file_id TEXT NOT NULL,
      drive_file_url TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_archive_entity ON entity_document_archive(entity_name);
    CREATE INDEX IF NOT EXISTS idx_archive_file_id ON entity_document_archive(drive_file_id);
    CREATE INDEX IF NOT EXISTS idx_archive_checksum ON entity_document_archive(sha256_checksum);
  `)

  const insertStmt = db.prepare(`
    INSERT INTO entity_document_archive (
      entity_name,
      document_type,
      file_name,
      file_path,
      sha256_checksum,
      drive_folder_path,
      drive_folder_id,
      drive_file_id,
      drive_file_url
    ) VALUES (
      ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
  `)

  const archivedFiles: ArchivalReportItem[] = []

  for (const item of uploadResults) {
    const relativePath = path.relative(".", item.fullPath).replace(/\\/g, "/")
    const res = insertStmt.run(
      ENTITY_NAME,
      item.meta.documentType,
      item.meta.fileName,
      relativePath,
      item.upload.sha256Checksum,
      TARGET_DRIVE_FOLDER,
      folderResult.folderId,
      item.upload.fileId,
      item.upload.driveUrl
    )

    const dbRecordId = res.lastInsertRowid
    console.log(`  - Recorded: [${item.meta.documentType}] ID=${dbRecordId} DriveFileID=${item.upload.fileId}`)

    archivedFiles.push({
      documentType: item.meta.documentType,
      fileName: item.meta.fileName,
      filePath: relativePath,
      sha256Checksum: item.upload.sha256Checksum,
      driveFolderId: folderResult.folderId,
      driveFileId: item.upload.fileId,
      driveFileUrl: item.upload.driveUrl,
      dbRecordId,
    })
  }

  db.close()
  console.log("\n[SUCCESS] All 3 formation documents uploaded and indexed into Vault DB.")
  return { folderResult, archivedFiles }
}

// Auto-run if executed directly
if (process.argv[1] && process.argv[1].endsWith("archive_luxury_decor_mcp.ts")) {
  executeLuxuryDecorArchival()
    .then(() => {
      process.exit(0)
    })
    .catch((err) => {
      console.error("[ERROR] Execution failed:", err)
      process.exit(1)
    })
}
