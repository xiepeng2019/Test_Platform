import React, { useEffect, useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  Tabs,
  FormInstance,
} from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from '../../locale';
import {
  getTestTask,
  listTaskConfigOptions,
  listServerOptions,
  TaskConfigOptions,
  ServerOptions,
  TestTask,
  TestTaskCreate,
} from '@/client';
import TabPane from '@arco-design/web-react/es/Tabs/tab-pane';
import TestTaskHistory from '../TaskHistory';
import CaseSelector from '../CaseSelector';

const FormItem = Form.Item;

export interface TestTaskModalFormProps {
  form: FormInstance;
  loading: boolean;
  visible: boolean;
  readOnly?: boolean;
  record?: TestTask;
  onCancel: () => void;
  onSubmit: (values: TestTaskCreate) => void;
}

function ModalForm(props: TestTaskModalFormProps) {
  const t = useLocale(locale);
  const { form, visible, readOnly, record, onCancel, onSubmit, loading } =
    props;

  const [activeTab, setActiveTab] = useState('1');
  const [task, setTask] = useState<TestTask>();
  const [configOptions, setConfigOptions] = useState<TaskConfigOptions[]>([]);
  const [serverOptions, setServerOptions] = useState<ServerOptions[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    const fetchTask = async () => {
      const [configRes, envRes] = await Promise.all([
        listTaskConfigOptions(),
        listServerOptions(),
      ]);
      setConfigOptions(configRes.data || []);
      setServerOptions(envRes.data || []);

      if (record?.id) {
        const res = await getTestTask({ path: { id: record.id } });
        setTask(res.data);
        form.setFieldsValue(res.data || {});
        setSelectedRowKeys(res.data.cases_index || []);
      } else {
        setTask(undefined);
        setSelectedRowKeys([]);
      }
    };
    fetchTask();
  }, [record?.id]);

  const handleFinish = (values: TestTask) => {
    onSubmit({ ...record, ...values, cases: selectedRowKeys });
  };

  return (
    <Modal
      title={
        readOnly
          ? t['task.form.detail']
          : record
          ? t['task.form.edit']
          : t['task.form.create']
      }
      style={{ width: '65vw',  }}
      visible={visible}
      onCancel={onCancel}
      onOk={props.form.submit}
      confirmLoading={loading}
      footer={readOnly ? null : undefined}
      autoFocus={false}
      focusLock={true}
    >
      <Form
        size="mini"
        form={props.form}
        onSubmit={handleFinish}
        labelCol={{ span: 12 }}
        wrapperCol={{ span: 12 }}
        layout="vertical"
      >
        <Tabs type={'line'} activeTab={activeTab} onChange={setActiveTab}>
          <TabPane key="1" title="任务信息">
            <FormItem
              label={t['task.columns.name']}
              field="name"
              rules={[{ required: true }]}
            >
              <Input
                placeholder={t['task.form.name.placeholder']}
                disabled={readOnly}
              />
            </FormItem>
            <FormItem label={t['task.columns.config_id']} field="config_id">
              <Select
                placeholder={t['task.form.config_id']}
                disabled={readOnly}
                options={configOptions.map((item) => ({
                  label: item.name,
                  value: item.id,
                }))}
              />
            </FormItem>
            <FormItem label={t['task.columns.server_id']} field="server_id">
              <Select
                placeholder={t['task.form.server_id.placeholder']}
                disabled={readOnly}
                options={serverOptions.map((item) => ({
                  label: item.name,
                  value: item.id,
                }))}
              />
            </FormItem>
            <FormItem
              label={t['task.columns.failed_continue']}
              field="failed_continue"
              rules={[{ required: true }]}
            >
              <Select
                placeholder={t['task.form.failed_continue.placeholder']}
                disabled={readOnly}
                options={[
                  { label: '是', value: 1 },
                  { label: '否', value: 0 },
                ]}
              />
            </FormItem>
            <FormItem
              label={t['task.columns.lark_notice']}
              field="lark_notice"
              tooltip={t['task.columns.lark_notice.tooltip']}
              rules={[{ required: true }]}
            >
              <Select
                placeholder={t['task.form.lark_notice.placeholder']}
                disabled={readOnly}
                options={[
                  { label: '是', value: 1 },
                  { label: '否', value: 0 },
                ]}
              />
            </FormItem>
            <FormItem
              label={t['task.columns.lark_subscribe']}
              field="lark_subscribe"
              style={{ height: 250 }}
            >
              <Select
                mode="multiple"
                allowClear={true}
                placeholder={t['task.form.lark_subscribe.placeholder']}
                disabled={readOnly}
              />
            </FormItem>
          </TabPane>
          <TabPane key="2" title="测试用例">
            <FormItem
              label={t['task.columns.case']}
              field="cases"
              wrapperCol={{ span: 24 }}
            >
              <CaseSelector
                selectedRowKeys={selectedRowKeys}
                onSelectedRowKeysChange={(keys) =>
                  setSelectedRowKeys(keys.map((item) => item.toString()))
                }
                taskId={record?.id}
                readonly={readOnly}
              />
            </FormItem>
          </TabPane>
          {task && (
            <TabPane key="3" title="测试记录">
              <TestTaskHistory task_id={task.id} />
            </TabPane>
          )}
        </Tabs>
      </Form>
    </Modal>
  );
}

export default ModalForm;
