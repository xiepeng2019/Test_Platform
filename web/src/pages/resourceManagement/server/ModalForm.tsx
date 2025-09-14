import { Server, ServerCreate } from '@/client';
import useLocale from '@/utils/useLocale';
import {
  Button,
  Divider,
  Form,
  FormInstance,
  Grid,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Tabs,
} from '@arco-design/web-react';
import React, { useEffect } from 'react';
import locale from './locale';
import TabPane from '@arco-design/web-react/es/Tabs/tab-pane';
import { IconApps, IconDelete, IconStorage } from '@arco-design/web-react/icon';

export interface ServerModalFormProps {
  form: FormInstance;
  loading: boolean;
  visible: boolean;
  readOnly?: boolean;
  record?: Server;
  onCancel: () => void;
  onSubmit: (values: ServerCreate) => void;
}

const ServerModalForm = (props: ServerModalFormProps) => {
  const t = useLocale(locale);
  const { visible, readOnly, record, onCancel, onSubmit, loading } = props;

  useEffect(() => {
    props.form.setFieldsValue(record || {});
  }, [record?.id, readOnly]);

  const handleFinish = (values: ServerCreate) => {
    onSubmit({ ...record, ...values });
  };

  return (
    <Modal
      visible={visible}
      title={
        readOnly
          ? t['table.operation.detail']
          : record
          ? t['table.operation.edit']
          : t['table.operation.new']
      }
      onCancel={onCancel}
      onOk={props.form.submit}
      confirmLoading={loading}
    >
      <Form
        size="mini"
        form={props.form}
        onSubmit={handleFinish}
        // layout="vertical"
        disabled={readOnly || loading}
        wrapperCol={{ span: 16 }}
        labelCol={{ span: 6 }}
      >
        <Tabs defaultActiveTab="1">
          <TabPane
            key="1"
            title={
              <span>
                <IconStorage style={{ marginRight: 6 }} />
                {t['server.pane.server.name']}
              </span>
            }
          >
            <Form.Item
              field="name"
              label={t['server.columns.name']}
              rules={[{ required: true }]}
              style={{ marginBottom: 0 }}
            >
              <Input placeholder="Server Name" />
            </Form.Item>
            <Divider orientation="left" style={{ margin: '2px 0' }}>
              Server
            </Divider>
            <Form.Item
              label={'IP'}
              rules={[{ required: true }]}
              style={{ marginBottom: 0 }}
            >
              <Grid.Row gutter={4}>
                <Grid.Col span={16}>
                  <Form.Item
                    field="ip"
                    required
                    rules={[
                      {
                        type: 'string',
                        required: true,
                        message: t['server.form.ip.validate.error'],
                        match: /^(\d{1,3}\.){3}\d{1,3}$/,
                      },
                    ]}
                  >
                    <Input placeholder="Server IP" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={8}>
                  <Form.Item
                    field="port"
                    rules={[{ required: true }]}
                    initialValue={'22'}
                  >
                    <InputNumber
                      min={1}
                      max={65535}
                      placeholder="Server SSH Server Port"
                    />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
            <Form.Item
              field="sn"
              label="SN"
              rules={[
                {
                  type: 'string',
                  required: true,
                  message: t['server.form.sn.validate.error'],
                  match: /^[A-Za-z0-9]{6,20}$/,
                },
              ]}
            >
              <Input placeholder="Server SN" />
            </Form.Item>
            <Form.Item
              label={`SSH ${t['server.form.username']}`}
              rules={[{ required: true }]}
              style={{ marginBottom: 0 }}
            >
              <Grid.Row gutter={4}>
                <Grid.Col span={8}>
                  <Form.Item
                    field="username"
                    rules={[{ required: true }]}
                    initialValue={'root'}
                  >
                    <Input placeholder="Server SSH Username" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={16}>
                  <Form.Item
                    field="password"
                    rules={[{ required: true }]}
                    initialValue={'Duduadmin@1234'}
                  >
                    <Input.Password placeholder="Server SSH Password" />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
            <Divider orientation="left" style={{ margin: '2px 0' }}>
              BMC
            </Divider>
            <Form.Item
              field="bmc_ip"
              label={'IP'}
              rules={[
                {
                  type: 'string',
                  required: true,
                  message: t['server.form.bmc_ip.validate.error'],
                  match: /^(\d{1,3}\.){3}\d{1,3}$/,
                },
              ]}
            >
              <Input placeholder="BMC Server IP" />
            </Form.Item>
            <Form.Item
              label={`SSH ${t['server.form.username']}`}
              rules={[{ required: true }]}
              style={{ marginBottom: 0 }}
            >
              <Grid.Row gutter={4}>
                <Grid.Col span={8}>
                  <Form.Item
                    field="bmc_username"
                    rules={[{ required: true }]}
                    initialValue={'root'}
                  >
                    <Input placeholder="BMC SSH Username" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={16}>
                  <Form.Item
                    field="bmc_password"
                    rules={[{ required: true }]}
                    initialValue={'Duduadmin@1234'}
                  >
                    <Input.Password placeholder="BMC SSH Password" />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
            <Form.Item
              label={`Web ${t['server.form.username']}`}
              style={{ marginBottom: 0 }}
            >
              <Grid.Row gutter={4}>
                <Grid.Col span={8}>
                  <Form.Item field="bmc_web_username" initialValue={'root'}>
                    <Input placeholder="BMC Web Username" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={16}>
                  <Form.Item
                    field="bmc_web_password"
                    initialValue={'Duduadmin@1234'}
                  >
                    <Input.Password placeholder="BMC Web Password" />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
            <Divider orientation="left" style={{ margin: '2px 0' }}>
              PSU
            </Divider>
            <Form.Item label="1" field="psu_1" style={{ marginBottom: 0 }}>
              <Grid.Row gutter={4}>
                <Grid.Col span={16}>
                  <Form.Item
                    field="psu_1.ip"
                    rules={[
                      {
                        required: true,
                        message: t['server.form.psu_ip.validate.error'],
                        match: /^(\d{1,3}\.){3}\d{1,3}$/,
                      },
                    ]}
                  >
                    <Input placeholder="IP" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={8}>
                  <Form.Item field="psu_1.outlet">
                    <InputNumber min={1} max={8} placeholder="Outlet" />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
            <Form.Item label="2" field="psu_2">
              <Grid.Row gutter={4}>
                <Grid.Col span={16}>
                  <Form.Item
                    field="psu_2.ip"
                    rules={[
                      {
                        required: true,
                        message: t['server.form.psu_ip.validate.error'],
                        match: /^(\d{1,3}\.){3}\d{1,3}$/,
                      },
                    ]}
                  >
                    <Input placeholder="IP" />
                  </Form.Item>
                </Grid.Col>
                <Grid.Col span={8}>
                  <Form.Item field="psu_2.outlet">
                    <InputNumber min={1} max={8} placeholder="Outlet" />
                  </Form.Item>
                </Grid.Col>
              </Grid.Row>
            </Form.Item>
          </TabPane>
          <TabPane
            key="2"
            title={
              <span>
                <IconApps style={{ marginRight: 6 }} />
                {t['server.pane.board.name']}
              </span>
            }
          >
            <Form.Item label={t['server.form.link_type']} field="link_type">
              <Select
                placeholder="Link type"
                options={[
                  {
                    label: 'Virtual',
                    value: 'virtual',
                  },
                  {
                    label: 'SSH',
                    value: 'ssh',
                  },
                  {
                    label: 'Telnet',
                    value: 'telnet',
                  },
                ]}
              />
            </Form.Item>
            <Form.List field="boards">
              {(fields, { add, remove, move }) => {
                console.log(fields);
                return (
                  <div>
                    {fields.map((item, index) => {
                      return (
                        <div key={item.key}>
                          <Form.Item label={'Board ' + index} style={{ marginBottom: 0 }}>
                            <Space>
                              <Form.Item
                                field={item.field + '.ip'}
                                rules={[
                                  {
                                    required: true,
                                    message:
                                      t['server.form.board_ip.validate.error'],
                                    match: /^(\d{1,3}\.){3}\d{1,3}$/,
                                  },
                                ]}
                              >
                                <Input placeholder="IP" />
                              </Form.Item>
                              <Form.Item
                                field={item.field + '.port'}
                                rules={[{ required: true }]}
                              >
                                <InputNumber
                                  min={1}
                                  max={65535}
                                  placeholder="Port"
                                />
                              </Form.Item>
                              {!readOnly && (
                                <Button
                                  icon={<IconDelete />}
                                  shape="circle"
                                  status="danger"
                                  onClick={() => remove(index)}
                                ></Button>
                              )}
                            </Space>
                          </Form.Item>
                        </div>
                      );
                    })}
                    <Form.Item wrapperCol={{ offset: 5 }}>
                      <Button
                        type="primary"
                        onClick={() => {
                          add();
                        }}
                      >
                        {t['server.form.add_board']}
                      </Button>
                    </Form.Item>
                  </div>
                );
              }}
            </Form.List>
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

export default ServerModalForm;
