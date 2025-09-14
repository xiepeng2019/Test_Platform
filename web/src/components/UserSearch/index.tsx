import React, { useState, useRef, useCallback } from 'react';
import {
  Select,
  Avatar,
  Spin,
  Tooltip,
  Tag,
  SelectProps,
} from '@arco-design/web-react';
import debounce from 'lodash/debounce';
import { searchUser, UserSearch } from '@/client';

interface Props extends Omit<SelectProps, 'value' | 'onChange'> {
  value?: string[]; // id[]
  onChange?: (value: string[]) => void;
}

export default function UserSearchGet({ value, onChange, ...rest }: Props) {
  const [options, setOptions] = useState<SelectProps['options']>([]);
  const [fetching, setFetching] = useState(false);
  const fetchIdRef = useRef(0);
  const userMapRef = useRef<Record<string, UserSearch>>({});

  const fetchUser = useCallback(
    debounce((input: string) => {
      fetchIdRef.current += 1;
      const currentId = fetchIdRef.current;
      setFetching(true);
      setOptions([]);

      searchUser({ query: { q: input } }).then((res) => {
        if (currentId !== fetchIdRef.current) return;

        const users = res.data;
        users.forEach((u) => {
          userMapRef.current[u.id] = u;
        });

        setOptions(
          users.map((user) => ({
            label: (
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <Avatar size={20} style={{ marginRight: 8 }}>
                  <img src={user.avatar} />
                </Avatar>
                {user.name}
              </div>
            ),
            value: user.id,
          }))
        );
        setFetching(false);
      });
    }, 400),
    []
  );

  const renderTag = (option) => {
    const user = userMapRef.current[option.value];
    return (
      <Tooltip content={user?.id}>
        <Tag
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            borderRadius: 12,
          }}
        >
          <Avatar size={16} style={{ marginRight: 4 }}>
            <img src={user?.avatar} />
          </Avatar>
          {user?.name || option.value}
        </Tag>
      </Tooltip>
    );
  };

  return (
    <Select
      showSearch
      maxTagCount={1}  // 后端表结构设计目前只支持搜索一个用户, 用的是 id in key 的方式
      placeholder="搜索用户"
      filterOption={false}
      value={value}
      onChange={onChange}
      onSearch={fetchUser}
      renderTag={renderTag}
      notFoundContent={
        fetching ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Spin style={{ margin: 12 }} />
          </div>
        ) : null
      }
      options={options}
      {...rest}
    />
  );
}
