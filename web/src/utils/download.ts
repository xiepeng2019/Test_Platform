import r from "./requests";


export const downloadRecordLogFile = async (
  recordId: number,
  onProgress?: (progress: number) => void // 新增进度回调
) => {
  const response = await r.get(
    `/api/test_task/record/${recordId}/log/download`,
    {
      responseType: 'blob',
      timeout: 1000 * 60 * 1,
      // 添加进度监听
      onDownloadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          onProgress(percent); // 触发进度回调
        }
      },
    }
  );

  const blob = new Blob([response.data], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;

  // 获取文件名（来自 Content-Disposition 头）
  const disposition = response.headers['content-disposition'];
  let filename = 'log.log';
  const match = /filename="?([^"]+)"?/.exec(disposition);
  if (match && match[1]) {
    filename = decodeURIComponent(match[1]);
  }

  link.setAttribute('download', filename);
  link.click();

  window.URL.revokeObjectURL(url);
};
