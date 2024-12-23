import React, { useState } from 'react';

function ExportDialog({ onExport }) {
  const [customFolderName, setCustomFolderName] = useState('');

  const handleExport = () => {
    onExport(customFolderName);
  };

  return (
    <div className="export-dialog">
      <div className="form-group">
        <label htmlFor="folderName">文件夹名称（可选）：</label>
        <input
          type="text"
          id="folderName"
          value={customFolderName}
          onChange={(e) => setCustomFolderName(e.target.value)}
          placeholder="留空将使用时间戳命名"
        />
      </div>
      <button onClick={handleExport}>导出</button>
    </div>
  );
}

export default ExportDialog; 