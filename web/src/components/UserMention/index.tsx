import React, {
  useState,
  useRef,
  useCallback,
  useEffect,
  ReactNode,
} from 'react';
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


interface UserSelectProps extends Omit<SelectProps, 'value' | 'onChange'> {
  value?: UserSearch[];
  onChange?: (value: UserSearch[]) => void;
}

function UserSelect({ value, onChange, ...rest }: UserSelectProps) {
  const [options, setOptions] = useState<{ label: ReactNode; value: string }[]>(
    []
  );
  const [fetching, setFetching] = useState(false);
  const refFetchId = useRef(null);
  const userMapRef = useRef<Record<string, UserSearch>>({});

  useEffect(() => {
    console.log(value);
    if (value) {
      value.forEach((user) => {
        userMapRef.current[user.email] = user;
      });
    }
  }, [value]);

  const debouncedFetchUser = useCallback(
    debounce((inputValue) => {
      refFetchId.current = Date.now();
      const fetchId = refFetchId.current;
      setFetching(true);
      setOptions([]);
      searchUser({ query: { q: inputValue } }).then((body) => {
        if (refFetchId.current !== fetchId) return;
        const userInfoList: UserSearch[] = body.data;
        userInfoList.forEach((user) => {
          userMapRef.current[user.email] = user;
        });

        const options = userInfoList.map((user) => ({
          label: (
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Avatar size={20} style={{ marginLeft: 2, marginRight: 10 }}>
                <img alt="avatar" src={user.avatar} />
              </Avatar>
              {user.name}
            </div>
          ),
          value: user.email,
        }));
        setFetching(false);
        setOptions(options);
      });
    }, 500),
    []
  );

  const renderTag = (option) => {
    const user = userMapRef.current[option.value as string];
    return (
      <Tooltip content={user?.email}>
        <Tag
          color="gray"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            borderRadius: 12,
          }}
        >
          <Avatar size={16} style={{ marginRight: 4 }}>
            <img src={user?.avatar} />
          </Avatar>
          {user?.name}
        </Tag>
      </Tooltip>
    );
  };

  return (
    <Select
      // className={styles['user-mention']}
      showSearch
      mode="multiple"
      options={options}
      placeholder="Search by name"
      filterOption={false}
      value={value?.map((user) => user.email)}
      onChange={(emailList) => {
        const selectedUsers = emailList
          .map((email) => userMapRef.current[email])
          .filter(Boolean);
        onChange?.(selectedUsers);
      }}
      renderTag={renderTag}
      onSearch={debouncedFetchUser}
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
      {...rest}
    />
  );
}

export default UserSelect;
