import React, { useContext } from 'react';
import { GlobalContext } from '@/context';
import { Form, Input, Button, Grid, Select } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import styles from './style/index.module.less';
import { IconRefresh, IconSearch } from '@arco-design/web-react/icon';

const { Row, Col } = Grid;
const FormItem = Form.Item;


export interface SearchFormProps {
  onSearch: (values: Record<string, any>) => void;
  labelCol?: { span: number };
  wrapperCol?: { span: number };
}

function SearchForm(props: SearchFormProps) {
  const t = useLocale(locale);
  const labelCol = props.labelCol || { span: 8 };
  const wrapperCol = props.wrapperCol || { span: 16 };

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
  const colSpan = lang === 'zh-CN' ? 7 : 10;

  return (
    <div className={styles['search-form-wrapper']}>
      <Form
        size="mini"
        form={form}
        className={styles['search-form']}
        labelAlign="left"
        layout="horizontal"
        style={{ padding: 0, margin: 0 }}
        labelCol={labelCol}
        wrapperCol={wrapperCol}
      >
        <Row gutter={24}>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.index']} field="index">
              <Input
                placeholder={t['case.columns.index.placeholder']}
                allowClear
              />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.name']} field="name">
              <Input
                placeholder={t['case.columns.name.placeholder']}
                allowClear
              />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.module']} field="module">
              <Input
                placeholder={t['case.columns.module.placeholder']}
                allowClear
              />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.automation']} field="automation">
              <Select
                placeholder={t['case.columns.automation.placeholder']}
                options={[
                  {
                    label: t['case.operations.automation.true'],
                    value: 1,
                  },
                  {
                    label: t['case.operations.automation.false'],
                    value: 0,
                  },
                ]}
                allowClear
              />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.automated']} field="automated">
              <Select
                placeholder={t['case.columns.automated.placeholder']}
                options={[
                  {
                    label: t['case.operations.automated.true'],
                    value: 1,
                  },
                  {
                    label: t['case.operations.automated.false'],
                    value: 0,
                  },
                ]}
                allowClear
              />
            </FormItem>
          </Col>
          <Col span={colSpan}>
            <FormItem label={t['case.columns.priority']} field="priority">
              <Select
                placeholder={t['case.columns.priority.placeholder']}
                options={[
                  {
                    label: 'P0',
                    value: 'P0',
                  },
                  {
                    label: 'P1',
                    value: 'P1',
                  },
                  {
                    label: 'P2',
                    value: 'P2',
                  },
                ]}
                allowClear
              />
            </FormItem>
          </Col>
        </Row>
      </Form>
      <div className={styles['right-button']}>
        <Button
          size="mini"
          type="primary"
          icon={<IconSearch />}
          onClick={handleSubmit}
        >
          {t['case.form.search']}
        </Button>
        <Button size="mini" icon={<IconRefresh />} onClick={handleReset}>
          {t['case.form.reset']}
        </Button>
      </div>
    </div>
  );
}

export default SearchForm;
