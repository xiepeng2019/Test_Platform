import React from 'react';
import {
  Button,
  Popconfirm,
  Space,
  TableColumnProps,
} from '@arco-design/web-react';
import { TaskConfigListItem } from '@/client';
import dayjs from 'dayjs';
import UserColumnRender from '@/components/UserColumn';
import { ActionType } from '@/utils/consts';

export function getColumns(
  callback: (record: TaskConfigListItem, action: ActionType) => void
): TableColumnProps<TaskConfigListItem>[] {
  return [
    {
      title: '名称',
      dataIndex: 'name',
    },
    {
      title: '说明',
      dataIndex: 'description',
    },
    {
      title: '创建人',
      dataIndex: 'owner',
      render: (record) => UserColumnRender([record]),
    },
    // {
    //   title: '关联任务',
    //   dataIndex: 'associate_tasks_count',
    // },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      render: (created_at) => {
        return dayjs(created_at).format('YYYY-MM-DD HH:mm:ss');
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      render: (updated_at) => {
        return dayjs(updated_at).format('YYYY-MM-DD HH:mm:ss');
      },
    },
    {
      title: '操作',
      dataIndex: 'operations',
      fixed: 'right' as const,
      width: 180,
      render: (_, record) => (
        <Space size="mini">
          <Button
            size="mini"
            status='success'
            onClick={() => callback(record, ActionType.DETAIL)}
          >
            详情
          </Button>
          <Button
            size="mini"
            status="warning"
            onClick={() => callback(record, ActionType.EDIT)}
          >
            编辑
          </Button>
          {/* 二次确认 */}
          <Popconfirm
            focusLock
            title="确认删除任务配置?"
            content="确认删除任务配置后，关联任务将无法使用该配置"
            onOk={() => {
              callback(record, ActionType.DELETE);
            }}
          >
            <Button size="mini" status="danger">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];
}
