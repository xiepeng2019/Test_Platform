import {
  Alert,
  Button,
  Checkbox,
  Link,
  Message,
  Modal,
  Space,
  Upload,
} from '@arco-design/web-react';
import React, { useState } from 'react';
import styles from './style/upload.modal.module.less';
import { IconMindMapping } from '@arco-design/web-react/icon';
import { importTestCaseFile, validateTestCaseFile } from '@/client';
import { isAxiosError } from '@/utils/requests';

export interface UploadModalFormProps {
  visible: boolean;
  onCancel: () => void;
  onOk: () => void;
}

const caseStatus = (response) => {
  switch (response.response.status) {
    case 400:
      console.error('字段缺失或无效：', response.error.detail);
      Modal.error({
        title: '校验失败, missing_fields',
        content: JSON.stringify(response.error.detail),
      });
      return { type: 'missing_fields', errors: response.error.detail };
    case 422:
      console.error('参数格式错误');
      return { type: 'validation_error', errors: response.error };
    case 500:
      console.error('系统错误：', response.error.detail);
      return { type: 'system_error', message: response.error.detail };
    default:
      console.warn('未知错误状态码：', response.response.status);
      return { type: 'unknown_error', status: response.response.status };
  }
};

const UploadModalForm = (props: UploadModalFormProps) => {
  const { visible, onCancel, onOk } = props;
  const [increment, setIncrement] = useState<boolean>(true);
  const [fileList, setFileList] = React.useState([]);
  const [isValid, setIsValid] = useState(false);

  const handleValidate = async () => {
    if (fileList.length === 0) return;

    try {
      const response = await validateTestCaseFile({
        body: { file: fileList[0].originFile },
      });

      if (response.error) {
        setIsValid(false);
        setFileList([]);
        if (!isAxiosError(response)) {
          Message.error('校验失败');
          return;
        }
        return caseStatus(response);
      } else if (response.data) {
        setIsValid(true);
        Message.success('文件校验通过');
      } else {
        setIsValid(false);
        Message.error('校验失败');
      }
    } catch (e) {
      Message.error('网络异常');
    }
  };

  const handleImport = async () => {
    if (fileList.length === 0) return;

    try {
      const res = await importTestCaseFile({
        body: { file: fileList[0].originFile },
        query: {
          increment: increment,
        },
      });

      if (res.error) {
        setIsValid(false);
        setFileList([]);
        Message.error('导入失败');
        return;
      }

      if (res.data) {
        Message.success('导入成功');
        onOk();
      }
    } catch (e) {
      Message.error('导入失败');
    }
  };

  return (
    <Modal
      className={styles['upload-modal']}
      title={'批量导入用例'}
      visible={visible}
      onCancel={() => {
        setFileList([]);
        setIsValid(false);
        onCancel();
      }}
      footer={null}
    >
      <Space
        direction="vertical"
        style={{
          width: '99%',
          maxHeight: '50vh',
          minHeight: '30vh',
          overflowX: 'hidden',
        }}
      >
        <Alert
          content="上传前请先按照用例模板格式编辑内容"
          action={
            <Link
              href="#"
              icon={<IconMindMapping />}
              onClick={() => Message.info('暂未支持')}
            >
              下载 Excel 模板
            </Link>
          }
        />
        <Upload
          drag
          multiple={false}
          accept=".xlsx"
          fileList={fileList}
          onChange={(_, file) => setFileList([file])}
          showUploadList={false}
          beforeUpload={() => {
            setIsValid(false);
            return true;
          }}
        >
          <div className={styles['upload-drag']}>
            {!fileList.length ? (
              <span>
                托拽或点击选择文件
              </span>
            ) : (
              <>
                <span>
                  {fileList[0].name}
                </span>
              </>
            )}
          </div>
        </Upload>
        <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Checkbox checked={increment} onChange={setIncrement} disabled={true}>
            用例编号相同时覆盖原用例
          </Checkbox>
          {!isValid ? (
            <Button disabled={!fileList.length} onClick={handleValidate}>
              校验文件
            </Button>
          ) : (
            <Button onClick={handleImport}>导入用例</Button>
          )}
        </Space>
      </Space>
    </Modal>
  );
};

export default UploadModalForm;
