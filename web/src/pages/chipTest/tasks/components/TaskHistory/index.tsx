import React, { useEffect, useState } from 'react';
import {
  Collapse,
  Tag,
  Divider,
  Popover,
  Skeleton,
  Button,
  Progress,
} from '@arco-design/web-react';

import { CaseRecord, listTestTaskRecord, TaskRecord } from '@/client';
import dayjs from 'dayjs';
import { Table, TableColumnProps } from '@arco-design/web-react';
import styles from './TaskHistory.module.less';
import { IconSchedule, IconCloudDownload } from '@arco-design/web-react/icon';
import { getCaseStatusLabel, getTaskStatusLabel } from '@/utils/Tags';
import { downloadRecordLogFile } from '@/utils/download';

const CollapseItem = Collapse.Item;

export interface TestTaskHistory {
  task_id: number;
}

function getPopoverContent(item: TaskRecord) {
  return (
    <span>
      <p style={{ color: 'green', marginBottom: 1 }}>通过：{item.passed}</p>
      <p style={{ color: 'red', marginBottom: 0 }}>失败：{item.failed}</p>
      <p style={{ color: 'gray', marginBottom: 0 }}>总数：{item.total}</p>
    </span>
  );
}

const columns: TableColumnProps[] = [
  {
    title: '用例编号',
    dataIndex: 'case_index',
  },
  {
    title: '开始时间',
    dataIndex: 'start_time',
    render: (start_at) => {
      if (!start_at) {
        return '-';
      }
      return dayjs(start_at).format('YYYY-MM-DD HH:mm:ss');
    },
  },
  {
    title: '结束时间',
    dataIndex: 'end_time',
    render: (end_at) => {
      if (!end_at) {
        return '-';
      }
      return dayjs(end_at).format('YYYY-MM-DD HH:mm:ss');
    },
  },
  {
    title: '测试耗时',
    dataIndex: 'duration',
    render: (duration) => {
      return (
        typeof duration === 'number' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <IconSchedule />
            {duration}s
          </div>
        )
      );
    },
  },
  {
    title: '测试结果',
    dataIndex: 'result',
    render: (result) => {
      if (!result) {
        return '-';
      }
      return getCaseStatusLabel(result);
    },
  },
];

const TestCaseResultTable = ({
  caseRecords,
}: {
  caseRecords: CaseRecord[];
}) => {
  return (
    <Table
      rowKey={'id'}
      columns={columns}
      data={caseRecords}
      style={{ border: '1px solid #e5e5e5', padding: 0 }}
    />
  );
};

function headerContent(item: TaskRecord) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <Tag>{item.id}</Tag>
      <Divider type="vertical" />
      <span>{dayjs(item.created_at).format('YYYY-MM-DD HH:mm:ss')}</span>
    </div>
  );
}

function TaskHistory(props: TestTaskHistory) {
  const [taskRecordInfo, setTaskRecordInfo] = useState<TaskRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [progressMap, setProgressMap] = useState<Record<number, number>>({}); // key: taskId

  function extraContent(
    item: TaskRecord,
    onLogClick: (record: TaskRecord) => void
  ) {
    const progress = progressMap[item.id] ?? 0;

    return (
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Popover position="lt" content={getPopoverContent(item)}>
          <div style={{ display: 'flex', gap: 0 }}>
            <Tag size="small" color="green">{item.passed}</Tag>
            <Tag size="small" color="red">{item.failed}</Tag>
            <Tag size="small" color="gray">{item.total}</Tag>
          </div>
        </Popover>
        <Divider type="vertical" />
        {item?.status && getTaskStatusLabel(item.status)}
        <Divider type="vertical" />
        {progress === 0 || progress === 100 ? (
          <Button icon={<IconCloudDownload />} onClick={() => onLogClick(item)}>
            日志
          </Button>
        ) : (
          <Progress size="mini" percent={progress} />
        )}
      </div>
    );
  }

  useEffect(() => {
    setLoading(true);
    listTestTaskRecord({ path: { id: props.task_id } })
      .then((res) => setTaskRecordInfo(res.data.list))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [props.task_id]);

  const handleDownload = (record: TaskRecord) => {
    downloadRecordLogFile(record.id, (progress) => {
      setProgressMap((prev) => ({ ...prev, [record.id]: progress }));
    });
  };

  return loading ? (
    <Skeleton />
  ) : (
    <Collapse
      style={{ maxHeight: '72vh', overflow: 'auto' }}
      defaultActiveKey={taskRecordInfo[0]?.id.toString()}
    >
      {taskRecordInfo.map((item) => (
        <CollapseItem
          className={styles['collapse-item-case-results']}
          key={item.id}
          header={headerContent(item)}
          name={item.id.toString()}
          extra={extraContent(item, handleDownload)}
        >
          <TestCaseResultTable caseRecords={item.case_records} />
        </CollapseItem>
      ))}
    </Collapse>
  );
}


export default TaskHistory;
