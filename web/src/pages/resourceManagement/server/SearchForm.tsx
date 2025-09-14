import React from 'react';
import useLocale from '@/utils/useLocale';
import {
  Form,
  Input,
  Button,
  Grid,
  FormInstance,
} from '@arco-design/web-react';
import { IconRefresh, IconSearch } from '@arco-design/web-react/icon';

export interface SearchFormProps {
  form: FormInstance;
  onSearch: () => void;
  onReset: () => void;
}

const SearchForm = ({ form, onSearch, onReset }: SearchFormProps) => {
  const gridSpan = 8;
  const t = useLocale();

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        gap: 10,
        borderBottom: '1px solid var(--color-border-1)',
        marginBottom: 10,
      }}
    >
      <Form
        form={form}
        id="searchForm"
        layout="vertical"
        size="mini"
        labelAlign="left"
      >
        <Grid.Row gutter={24}>
          <Grid.Col span={gridSpan}>
            <Form.Item label={t['table.columns.name']} field="name">
              <Input />
            </Form.Item>
          </Grid.Col>
          <Grid.Col span={gridSpan}>
            <Form.Item label="IP" field="ip">
              <Input />
            </Form.Item>
          </Grid.Col>
          <Grid.Col span={gridSpan}>
            <Form.Item label="SN" field="sn">
              <Input />
            </Form.Item>
          </Grid.Col>
        </Grid.Row>
      </Form>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          justifyContent: 'space-around',
          borderLeft: '1px solid var(--color-border-2)',
          padding: 10,
        }}
      >
        <Button
          size="small"
          type="primary"
          icon={<IconSearch />}
          onClick={onSearch}
        >
          {t['searchForm.search']}
        </Button>
        <Button
          size="small"
          type="default"
          icon={<IconRefresh />}
          onClick={onReset}
        >
          {t['searchForm.reset']}
        </Button>
      </div>
    </div>
  );
};

export default SearchForm;
