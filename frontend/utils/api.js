/**
 * Client utility for interacting with the FastAPI Assessment Backend.
 */

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://vedaai-assessment-f7ds.onrender.com/api').replace(/\/$/, '');

export async function uploadAssessmentFiles(questionPaperFile, answerSheetFile) {
  const formData = new FormData();
  formData.append('question_paper', questionPaperFile);
  formData.append('answer_sheet', answerSheetFile);

  const res = await fetch(`${API_BASE}/assessments`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Upload failed with status ${res.status}`);
  }

  return await res.json(); // { assessment_id: "...", status: "uploaded" }
}

export async function startProcessing(assessmentId) {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}/process`, {
    method: 'POST',
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Process start failed with status ${res.status}`);
  }

  return await res.json();
}

export async function getAssessmentStatus(assessmentId) {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}/status`);
  if (!res.ok) {
    throw new Error(`Failed to fetch status: ${res.status}`);
  }
  return await res.json(); // { assessment_id, status, stage, progress }
}

export async function getAssessmentResult(assessmentId) {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}`);
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to fetch result: ${res.status}`);
  }
  return await res.json();
}

export async function pollAssessmentUntilComplete(assessmentId, onProgress, intervalMs = 800) {
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const stat = await getAssessmentStatus(assessmentId);
        if (onProgress) {
          onProgress(stat);
        }

        if (stat.status === 'completed') {
          clearInterval(interval);
          const finalResult = await getAssessmentResult(assessmentId);
          resolve(finalResult);
        } else if (stat.status === 'failed') {
          clearInterval(interval);
          reject(new Error(stat.error || 'Assessment processing failed.'));
        }
      } catch (err) {
        clearInterval(interval);
        reject(err);
      }
    }, intervalMs);
  });
}
