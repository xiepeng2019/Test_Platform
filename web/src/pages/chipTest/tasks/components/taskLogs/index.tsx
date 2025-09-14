import React, { useEffect } from 'react';
import { Modal } from '@arco-design/web-react';
import styles from './index.module.less';
import { LazyLog } from 'react-lazylog';
import { TestTask } from '@/client';

const TaskLogPage = (props: {
  record: TestTask;
  visible: boolean;
  onCancel: () => void;
}) => {
  const { record, visible, onCancel } = props;

  useEffect(() => {
    if (!visible) return;
  }, [record?.id, visible]);

  return (
    <Modal
      visible={visible}
      onCancel={onCancel}
      className={styles['test-plan-card']}
      title={`任务日志 (ID: ${record?.id})`}
      style={{ width: '90vw' }}
    >
      <LazyLog
        className={styles['log-container']}
        lineClassName={styles['line']}
        url={`${window.env.REACT_APP_API_BASE_URL}/api/test_task/${record?.id}/log/stream`}
        stream={true}
        // enableSearch={true}
        follow={true}
        itemSize={35}
        height={window.innerHeight * 0.8 - 170}
        enableWrapping={false} // ❗禁用自动换行
        containerStyle={{
          backgroundColor: 'rgba(249,249,249)',
          borderRight: '10px',
          color: 'black',
          fontFamily: 'monospace',
          fontSize: 12,
          whiteSpace: 'nowrap',
          overflowX: 'scroll',
          padding: '10px',
        }}
        selectableLines
      />
    </Modal>
  );
};

export default TaskLogPage;
