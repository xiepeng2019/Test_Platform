import React, { useContext } from 'react';
import { GlobalContext } from '@/context';
import { Form, Input, Button, Grid } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import styles from './style/index.module.less';
import { IconRefresh, IconSearch } from '@arco-design/web-react/icon';
import UserSearchGet from '@/components/UserSearch';

const { Row, Col } = Grid;
const FormItem = Form.Item;

function SearchForm(props: { onSearch: (values: Record<string, any>) => void }) {
  const t = useLocale(locale);
  const [form] = Form.useForm();

  const handleSubmit = () => {
    const values = form.getFieldsValue();
    props.onSearch(values);
  };

  const handleReset = () => {
    form.resetFields();
    props.onSearch({});
  };

  const { lang } = useContext(GlobalContext);
  const colSpan = lang === 'zh-CN' ? 8 : 12;

  return (
    <div className={styles['search-form-wrapper']}>
      <Form
        size='mini'
        form={form}
        className={styles['search-form']}
        labelAlign="left"
        labelCol={{ span: 5 }}
        wrapperCol={{ span: 19 }}
      >
        <Row gutter={24}>
          <Col span={colSpan}>
            <FormItem label={t['project.form.name']} field="name">
              <Input placeholder={t['project.form.name.placeholder']} allowClear />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['project.form.owner']} field="owners">
              <UserSearchGet placeholder={t['project.form.owner.placeholder']} allowClear />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['project.form.git_repo']} field="git_repo">
              <Input placeholder={t['project.form.git_repo.placeholder']} allowClear />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['project.form.branch']} field="branch">
              <Input placeholder={t['project.form.branch.placeholder']} allowClear />
            </FormItem>
          </Col>
        </Row>
      </Form>
      <div className={styles['right-button']}>
        <Button type="primary" icon={<IconSearch />} onClick={handleSubmit}>
          {t['project.form.search']}
        </Button>
        <Button icon={<IconRefresh />} onClick={handleReset}>
          {t['project.form.reset']}
        </Button>
      </div>
    </div>
  );
}

export default SearchForm;