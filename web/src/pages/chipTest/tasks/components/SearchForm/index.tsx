import React, { useContext } from 'react';
import { GlobalContext } from '@/context';
import { Form, Input, Button, Grid, FormInstance } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from '../../locale';
import styles from './SearchForm.module.less';
import { IconRefresh, IconSearch } from '@arco-design/web-react/icon';
import UserSearchGet from '@/components/UserSearch';


export interface SearchFormProps {
  form: FormInstance;
  onSearch: (params: Record<string, any>) => void;
  onReset: () => void;
}

function SearchForm({ form, onSearch, onReset }: SearchFormProps) {
  const t = useLocale(locale);

  const { lang } = useContext(GlobalContext);
  const colSpan = lang === 'zh-CN' ? 8 : 12;

  return (
    <div className={styles['search-form-wrapper']}>
      <Form
        size='mini'
        form={form}
        className={styles['search-form']}
        labelAlign="left"
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 18 }}
      >
        <Grid.Row gutter={24}>
          <Grid.Col span={colSpan}>
            <Form.Item label={t['task.columns.name']} field="name">
              <Input placeholder={t['task.columns.name']} allowClear />
            </Form.Item>
          </Grid.Col>
          <Grid.Col span={colSpan}>
            <Form.Item label={t['task.columns.owner']} field="owner">
              <UserSearchGet placeholder={t['project.form.owner.placeholder']} allowClear />
            </Form.Item>
          </Grid.Col>
          <Grid.Col span={colSpan}>
            <Form.Item label={t['task.columns.status']} field="status">
              <Input placeholder={t['task.columns.status']} allowClear />
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
}

export default SearchForm;