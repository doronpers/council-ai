/**
 * ExportMenu Component - Export consultation results
 */
import React from 'react';
import type { ConsultationResult } from '../../types';
import { exportToMarkdown, exportToJson, downloadFile } from '../../utils/export';
import { useNotifications } from '../Layout/NotificationContainer';

interface ExportMenuProps {
  result: ConsultationResult;
}

const ExportMenu: React.FC<ExportMenuProps> = ({ result }) => {
  const { showNotification } = useNotifications();

  const handleExportMarkdown = () => {
    const content = exportToMarkdown(result);
    downloadFile(content, 'consultation.md', 'text/markdown');
    showNotification('Exported markdown', 'success');
  };

  const handleExportJson = () => {
    const content = exportToJson(result);
    downloadFile(content, 'consultation.json', 'application/json');
    showNotification('Exported JSON', 'success');
  };

  const handleCopySynthesis = () => {
    if (!result.synthesis) {
      showNotification('No synthesis available', 'info');
      return;
    }
    navigator.clipboard.writeText(result.synthesis).then(
      () => showNotification('Synthesis copied', 'success'),
      () => showNotification('Failed to copy synthesis', 'error')
    );
  };

  return (
    <div className="results-export-menu">
      <button type="button" className="btn btn-secondary" onClick={handleExportMarkdown}>
        Export Markdown
      </button>
      <button type="button" className="btn btn-secondary" onClick={handleExportJson}>
        Export JSON
      </button>
      <button type="button" className="btn btn-secondary" onClick={handleCopySynthesis}>
        Copy Synthesis
      </button>
    </div>
  );
};

export default ExportMenu;
