import React from 'react';
import { ServerStatus, UserSearch } from '@/client';
import UserColumnRender from '@/components/UserColumn';

import dayjs from 'dayjs';
import useLocale from '@/utils/useLocale';
import { Tag } from '@arco-design/web-react';

const statusColor: Record<ServerStatus, string> = {
  [ServerStatus.UNKNOWN]: 'gray',
  [ServerStatus.IDLE]: 'green',
  [ServerStatus.IN_USE]: 'orange',
  [ServerStatus.MAINTENANCE]: 'orange',
  [ServerStatus.ERROR]: 'red',
};

export const getBaseColumns = (t: ReturnType<typeof useLocale>) => {
  return [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t['table.columns.name'],
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: t['server.columns.status'],
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: ServerStatus) => {
        return <Tag color={statusColor[status]}>{status}</Tag>;
      },
    },
    {
      title: 'IP',
      dataIndex: 'ip',
      key: 'ip',
      width: 120,
    },
    {
      title: 'SN',
      dataIndex: 'sn',
      key: 'sn',
      width: 120,
    },
    {
      title: 'BMC IP',
      dataIndex: 'bmc_ip',
      key: 'bmc_ip',
      width: 120,
    },
    {
      title: t['table.columns.owner'],
      dataIndex: 'owner',
      key: 'owner',
      width: 120,
      render: (owner: UserSearch) => UserColumnRender([owner]),
    },
    {
      title: t['table.columns.createAt'],
      dataIndex: 'created_at',
      key: 'created_at',
      render: (created_at: string) =>
        dayjs(created_at).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t['table.columns.updateAt'],
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (updated_at: string) =>
        dayjs(updated_at).format('YYYY-MM-DD HH:mm:ss'),
    },
  ];
};
