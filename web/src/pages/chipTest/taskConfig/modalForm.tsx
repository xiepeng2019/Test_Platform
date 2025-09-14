import React from 'react';
import {
  Button,
  Form,
  FormInstance,
  Input,
  Modal,
  Space,
} from '@arco-design/web-react';
import FormItem from '@arco-design/web-react/es/Form/form-item';
import { IconDelete } from '@arco-design/web-react/icon';

export interface ModalFormProps {
  visible: boolean;
  onCancel: () => void;
  onOk: () => void;
  form: FormInstance;
  readonly: boolean;
}

function ModalForm(props: ModalFormProps) {
  return (
    <Modal
      title="新建配置"
      visible={props.visible}
      onOk={props.onOk}
      onCancel={props.onCancel}
      autoFocus={false}
      focusLock={true}
      style={{
        width: '50vw',
      }}
    >
      <Form
        form={props.form}
        disabled={props.readonly}
        autoComplete="off"
        style={{
          height: '50vh',
          overflowX: 'hidden',
          overflowY: 'auto',
          paddingRight: 10,
        }}
        validateMessages={{
          required: (_, { label }) => `${label}不能为空`,
        }}
      >
        <FormItem
          label="配置名称"
          field="name"
          required
          rules={[{ required: true, type: 'string' }]}
        >
          <Input placeholder="请输入配置名称" />
        </FormItem>
        <FormItem
          label="配置描述"
          field="description"
          rules={[{ required: true, type: 'string' }]}
        >
          <Input.TextArea placeholder="请输入配置描述" />
        </FormItem>
        <Form.List field="env_vars">
          {(fields, { add, remove, move }) => {
            return (
              <div>
                {fields.map((item, index) => {
                  return (
                    <div key={item.key}>
                      <Form.Item label={'变量 ' + index}>
                        <Space>
                          <Form.Item
                            field={item.field + '.name'}
                            rules={[{ required: true }]}
                            noStyle
                          >
                            <Input placeholder="请输入环境变量名称" />
                          </Form.Item>
                          <Form.Item
                            field={item.field + '.value'}
                            rules={[{ required: true, type: 'string' }]}
                            noStyle
                          >
                            <Input placeholder="请输入环境变量值" />
                          </Form.Item>
                          <Button
                            icon={<IconDelete />}
                            shape="circle"
                            status="danger"
                            disabled={props.readonly}
                            onClick={() => remove(index)}
                          ></Button>
                        </Space>
                      </Form.Item>
                    </div>
                  );
                })}
                <Form.Item wrapperCol={{ offset: 5 }}>
                  <Button
                    onClick={() => {
                      add();
                    }}
                  >
                    添加环境变量
                  </Button>
                </Form.Item>
              </div>
            );
          }}
        </Form.List>
      </Form>
    </Modal>
  );
}

export default ModalForm;
