import React, { useEffect } from 'react';
import { Button, Card, Form, Message, Table } from '@arco-design/web-react';
import { getColumns } from './constants';
import ModalForm from './modalForm';
import {
  createTaskConfig,
  deleteTaskConfig,
  listTaskConfigs,
  TaskConfigListItem,
  updateTaskConfig,
} from '@/client';
import { ActionType } from '@/utils/consts';
import { IconPlus } from '@arco-design/web-react/icon';

const App = () => {
  const [data, setData] = React.useState<TaskConfigListItem[]>([]);
  const [visible, setVisible] = React.useState(false);
  const [readonly, setReadonly] = React.useState(false);
  const [record, setRecord] = React.useState<TaskConfigListItem>();
  const [action, setAction] = React.useState<ActionType>(ActionType.DETAIL);
  const [form] = Form.useForm<TaskConfigListItem>();

  const fetchData = async () => {
    const { data, error } = await listTaskConfigs();
    if (error) {
      return;
    }
    setData(data.list);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onDelete = (record: TaskConfigListItem) => {
    deleteTaskConfig({ path: { task_config_id: record?.id } }).then((res) => {
      if (res.error) {
        Message.error('删除失败');
        return;
      } else {
        Message.success('删除成功');
        setRecord(undefined);
        setAction(ActionType.DETAIL);
        setVisible(false);
        fetchData();
      }
    });
  };

  const onModalOk = async () => {
    if (action === ActionType.CREATE) {
      try {
        await form
          .validate()
          .then((values) => {
            return createTaskConfig({ body: values });
          })
          .then((res) => {
            if (res.error) {
              Message.error('创建失败');
              return;
            } else {
              Message.success('创建成功');
              fetchData();
            }
            setVisible(false);
            setRecord(undefined);
          });
      } catch (error) {
        Message.error('校验失败');
      }
    } else if (action === ActionType.EDIT) {
      const newRecord = { ...form.getFieldsValue() };
      updateTaskConfig({
        path: { task_config_id: record?.id },
        body: {
          name: newRecord.name,
          description: newRecord.description,
          env_vars: newRecord.env_vars,
        },
      }).then((res) => {
        if (res.error) {
          Message.error('更新失败');
          return;
        } else {
          Message.success('更新成功');
          setAction(ActionType.DETAIL);
          fetchData();
          setVisible(false);
          setRecord(undefined);
        }
      });
    }
    setReadonly(false);
  };

  const handleAction = (record: TaskConfigListItem, action: ActionType) => {
    setAction(action);
    setRecord(record);
    switch (action) {
      case ActionType.DETAIL:
        form.setFieldsValue(record);
        setReadonly(true);
        setVisible(true);
        break;
      case ActionType.EDIT:
        form.setFieldsValue(record);
        setReadonly(false);
        setVisible(true);
        break;
      case ActionType.DELETE:
        onDelete(record);
        break;
      case ActionType.CREATE:
        form.setFieldsValue({
          name: '',
          description: '',
          env_vars: [],
        });
        setReadonly(false);
        setVisible(true);
        break;
    }
  };

  return (
    <Card>
      <div
        style={{
          display: 'flex',
          justifyContent: 'flex-start',
          marginBottom: 10,
        }}
      >
        <Button
          size="mini"
          type="primary"
          icon={<IconPlus />}
          onClick={() => handleAction(undefined, ActionType.CREATE)}
        >
          新建
        </Button>
      </div>
      <Table<TaskConfigListItem>
        size="mini"
        columns={getColumns(handleAction)}
        data={data}
        rowKey={(record) => record.id}
      />
      <ModalForm
        visible={visible}
        readonly={readonly}
        onCancel={() => {
          setVisible(false);
          setAction(ActionType.DETAIL);
        }}
        onOk={onModalOk}
        form={form}
      />
    </Card>
  );
};

export default App;
