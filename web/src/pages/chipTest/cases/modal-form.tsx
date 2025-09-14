import React from 'react';
import {
  Modal,
  Form,
  Input,
  Message,
  Select,
  InputNumber,
} from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import { createTestCase, updateTestCase } from '@/client';

const FormItem = Form.Item;
const Option = Select.Option;

function AddForm({ visible, onCancel, onOk, testCase, readOnly }) {
  const t = useLocale(locale);
  const [form] = Form.useForm();

  React.useEffect(() => {
    if (testCase) {
      console.log('testCase', testCase);
      form.setFieldsValue(testCase);
    } else {
      form.resetFields();
    }
  }, [form, testCase]);

  const handleSubmit = async () => {
    const values = await form.validate();
    if (testCase) {
      const { error } = await updateTestCase({
        path: {
          id: testCase.id,
        },
        body: values,
      });
      if (error) {
        Message.error(t['case.operations.edit.fail']);
        return;
      }
      Message.success(t['case.operations.edit.success']);
      form.resetFields();
      onOk();
      return;
    } else {
      const { error } = await createTestCase({
        body: values,
      });
      if (error) {
        Message.error(t['case.operations.create.fail']);
        return;
      }
      Message.success(t['case.operations.create.success']);
      form.resetFields();
      onOk();
      return;
    }
  };

  return (
    <Modal
      title={
        readOnly
          ? t['case.form.detail']
          : testCase
          ? t['case.form.edit']
          : t['case.form.add']
      }
      visible={visible}
      onOk={handleSubmit}
      onCancel={onCancel}
      footer={readOnly ? null : undefined}
      autoFocus={false}
      focusLock={true}
    >
      <Form
        form={form}
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 16 }}
        size="mini"
      >
        <FormItem
          label={t['case.columns.name']}
          field="name"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['case.form.name.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['case.columns.index']}
          field="index"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['case.form.index.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['case.columns.objective']}
          field="objective"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['case.form.objective.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['case.columns.priority']}
          field="priority"
          rules={[{ required: true }]}
        >
          <Select
            allowClear
            placeholder={t['case.form.priority.placeholder']}
            disabled={readOnly}
          >
            {['P0', 'P1', 'P2'].map((option) => (
              <Option key={`${option}`} value={option}>
                {option}
              </Option>
            ))}
          </Select>
        </FormItem>
        <FormItem label={t['case.columns.automation']} field="automation">
          <Select
            allowClear
            placeholder={t['case.form.automation.placeholder']}
            disabled={readOnly}
          >
            {[
              t['case.operations.automation.false'],
              t['case.operations.automation.true'],
            ].map((option, index) => (
              <Option key={`${option}`} value={index}>
                {option}
              </Option>
            ))}
          </Select>
        </FormItem>
        <FormItem label={t['case.columns.automated']} field="automated">
          <Select
            allowClear
            placeholder={t['case.form.automated.placeholder']}
            disabled={readOnly}
          >
            {[
              t['case.operations.automated.false'],
              t['case.operations.automated.true'],
            ].map((option, index) => (
              <Option key={`${option}`} value={index}>
                {option}
              </Option>
            ))}
          </Select>
        </FormItem>
        <FormItem label={t['case.columns.setup']} field="setup">
          <Input.TextArea
            maxLength={{ length: 200, errorOnly: true }}
            showWordLimit
          />
        </FormItem>
        <FormItem label={t['case.columns.step']} field="step">
          <Input.TextArea
            maxLength={{ length: 200, errorOnly: true }}
            showWordLimit
          />
        </FormItem>
        <FormItem label={t['case.columns.expected']} field="expected">
          <Input placeholder={t['case.form.expected']} disabled={readOnly} />
        </FormItem>
        <FormItem label={t['case.columns.topo']} field="topo">
          <Input placeholder={t['case.form.topo']} disabled={readOnly} />
        </FormItem>
      </Form>
    </Modal>
  );
}

export default AddForm;
