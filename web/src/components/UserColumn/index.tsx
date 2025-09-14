import React from 'react';

import { Avatar, Tag, Tooltip } from '@arco-design/web-react';
import { UserSearch } from '@/client';


interface UserTagProps {
  record: UserSearch;
  key?: number;
}

interface UserListTagProps {
  record: UserSearch[];
}

const UserTag = ({ record }: UserTagProps) => {
  return (
    <Tooltip content={record?.email}>
      <Tag
        color="gray"
        style={{
          borderRadius: 10,
          display: 'inline-flex',
          alignItems: 'center',
          padding: '4px 5px 5px 2px',
        }}
      >
        <Avatar size={22} style={{ marginRight: 4, marginLeft: 0 }}>
          <img src={record?.avatar} />
        </Avatar>
        {record?.name}
      </Tag>
    </Tooltip>
  );
};

const UserColumnRender = (records: UserSearch[]) => {
  if (!records) {
    return null;
  }
  return (
    <div>
      {records.map((user) => (
        <UserTag key={user.id} record={user} />
      ))}
    </div>
  );
};

export default UserColumnRender;
