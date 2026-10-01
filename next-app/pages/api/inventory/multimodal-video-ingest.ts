import type { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export const config = {
  api: {
    bodyParser: false,
  },
};

interface IngestResponse {
  status: string;
  items_cataloged: number;
  vault_path: string;
  error?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<IngestResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      status: 'rejected',
      items_cataloged: 0,
      vault_path: '',
      error: 'Method not allowed. POST required.',
    });
  }

  const uploadDir = path.join(process.cwd(), 'uploads', 'walkthroughs');
  fs.mkdirSync(uploadDir, { recursive: true });

  const form = formidable({
    uploadDir,
    keepExtensions: true,
    maxFileSize: 500 * 1024 * 1024,
  });

  form.parse(req, async (err, fields, files) => {
    if (err) {
      return res.status(500).json({
        status: 'error',
        items_cataloged: 0,
        vault_path: '',
        error: 'Failed to process video stream buffer.',
      });
    }

    const uploadedFile = Array.isArray(files.walkthrough_video)
      ? files.walkthrough_video[0]
      : files.walkthrough_video;

    if (!uploadedFile) {
      return res.status(400).json({
        status: 'error',
        items_cataloged: 0,
        vault_path: '',
        error: 'No video payload detected in request.',
      });
    }

    const videoPath = uploadedFile.filepath;
    const vaultPath = '/home/jupyter/Goings-OS/financial_vault.duckdb';

    try {
      const workerCommand = `python3 /home/jupyter/Goings-OS/tools/video/ingest_inventory_worker.py --video "${videoPath}" --db "${vaultPath}"`;
      const { stdout } = await execPromise(workerCommand);
      const parsedOutput = JSON.parse(stdout.trim());

      return res.status(200).json({
        status: 'success',
        items_cataloged: parsedOutput.items_cataloged || 0,
        vault_path: vaultPath,
      });
    } catch (workerError: any) {
      return res.status(500).json({
        status: 'error',
        items_cataloged: 0,
        vault_path: vaultPath,
        error: workerError.message || 'Worker ingestion failure.',
      });
    }
  });
}