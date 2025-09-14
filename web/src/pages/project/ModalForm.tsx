import React from 'react';
import { Modal, Form, Input, Message } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import UserSelect from '@/components/UserMention';
import { createProject, updateProject } from '@/client';

const FormItem = Form.Item;

function AddForm({ visible, onCancel, onOk, project, readOnly }) {
  const t = useLocale(locale);
  const [form] = Form.useForm();

  React.useEffect(() => {
    if (project) {
      form.setFieldsValue(project);
    } else {
      form.resetFields();
    }
  }, [project]);

  const handleSubmit = async () => {
    const values = await form.validate();
    if (project) {
      const { error } = await updateProject({
        path: {
          id: project.id,
        },
        body: values,
      })
      if (error) {
        Message.error('编辑失败');
        return;
      }
      Message.success('Success');
      form.resetFields();
      onOk();
    } else {
      const { error } = await createProject({
        body: values,
      })
      if (error) {
        Message.error('新建失败');
        return;
      }
      Message.success('Success');
      form.resetFields();
      onOk();
    }
  };

  return (
    <Modal
      title={
        readOnly
          ? t['project.form.detail']
          : project
          ? t['project.form.edit']
          : t['project.form.add']
      }
      visible={visible}
      onOk={handleSubmit}
      onCancel={onCancel}
      footer={readOnly ? null : undefined}
      autoFocus={false}
      focusLock={true}
    >
      <Form form={form} labelCol={{ span: 6 }} wrapperCol={{ span: 16 }}>
        <FormItem
          label={t['project.columns.name']}
          field="name"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['project.form.name.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['project.columns.gitRepository']}
          field="git_repo"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['project.form.git_repo.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['project.columns.branch']}
          field="branch"
          rules={[{ required: true }]}
        >
          <Input
            placeholder={t['project.form.branch.placeholder']}
            disabled={readOnly}
          />
        </FormItem>
        <FormItem
          label={t['project.columns.owner']}
          field="owners"
          rules={[{ required: true }]}
        >
          <UserSelect
            placeholder={t['project.form.owner.placeholder']}
            allowClear
            disabled={readOnly}
          />
        </FormItem>
        <FormItem label={t['project.columns.qa']} field="qas">
          <UserSelect
            placeholder={t['project.form.qa.placeholder']}
            allowClear
            disabled={readOnly}
          />
        </FormItem>
        <FormItem label={t['project.columns.dev']} field="devs">
          <UserSelect
            placeholder={t['project.form.dev.placeholder']}
            allowClear
            disabled={readOnly}
          />
        </FormItem>
      </Form>
    </Modal>
  );
}

export default AddForm;
