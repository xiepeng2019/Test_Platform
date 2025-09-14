import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Tree,
  Input,
  Dropdown,
  Menu,
  Modal,
  Form,
  Message,
  Button,
  Space,
  Badge,
  Tooltip,
} from '@arco-design/web-react';
import {
  IconPlus,
  IconMore,
  IconExpand,
  IconShrink,
  IconDelete,
  IconEdit,
  IconFolderAdd,
} from '@arco-design/web-react/icon';
import styles from './style/index.module.less';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import {
  NodeInstance,
  NodeProps,
} from '@arco-design/web-react/es/Tree/interface';
import { GlobalState } from '@/store';
import {
  createTestCaseNode,
  deleteTestCaseNode,
  getTestCase,
  listTestCaseNodeTree,
  updateTestCase,
  updateTestCaseNode,
} from '@/client';
import Row from '@arco-design/web-react/es/Grid/row';
import Col from '@arco-design/web-react/es/Grid/col';
import { TreeUtils } from '@/utils/treeUtils';

const generatorTreeNodes = (treeData) => {
  return treeData.map((item) => {
    const { children, key, ...rest } = item;
    return (
      <Tree.Node key={key} {...rest} dataRef={item}>
        {children ? generatorTreeNodes(item.children) : null}
      </Tree.Node>
    );
  });
};

export interface SearchTreeProps {
  onCheckedKeysChange: (
    checkedKeys: string[] | number[],
    checkedNodes?: NodeInstance
  ) => void;
  readonly?: boolean;
  renderExtra?: (props: NodeProps) => React.ReactNode;
}

function SearchTree(props: SearchTreeProps) {
  const onCheckedKeysChange = props.onCheckedKeysChange;
  const [treeData, setTreeData] = useState<NodeProps[]>([]);
  const [originalTreeData, setOriginalTreeData] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' or 'edit'
  const [currentNode, setCurrentNode] = useState(null);
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const t = useLocale(locale);
  const treeUtils = new TreeUtils();
  const caseUpdate = useSelector((state: GlobalState) => state.caseUpdate);

  useEffect(() => {
    fetchTreeData();
  }, [caseUpdate]);

  useEffect(() => {
    if (inputValue) {
      const result = treeUtils.searchData(inputValue, originalTreeData);
      setTreeData(result);
    } else {
      setTreeData(originalTreeData);
    }
  }, [inputValue, originalTreeData]);

  const fetchTreeData = async () => {
    try {
      const { data, error } = await listTestCaseNodeTree();
      if (error) {
        Message.error('获取树形数据失败');
        return;
      }
      setTreeData(data);
      setOriginalTreeData(data);
    } catch (error) {
      console.error('Failed to fetch tree data:', error);
      Message.error('获取树形数据失败');
    }
  };

  const addRootNode = async (name: string) => {
    const { error } = await createTestCaseNode({
      body: {
        name: name,
        parent_id: 0,
      },
    });
    if (error) {
      Message.error('创建失败');
      return;
    }
    Message.success('新增成功');
    fetchTreeData();
  };

  const handleAddRootNode = () => {
    setModalMode('add-root-node');
    setModalVisible(true);
  };

  const addNode = async (key: number, name: string) => {
    const { error } = await createTestCaseNode({
      body: {
        name: name,
        parent_id: key,
      },
    });
    if (error) {
      Message.error('创建失败');
      return;
    }
    Message.success('新增成功');
    fetchTreeData();
  };

  const updateNode = async (key: number, name: string) => {
    const { error } = await updateTestCaseNode({
      path: {
        id: key,
      },
      body: {
        name: name,
      },
    });
    if (error) {
      Message.error('修改失败');
      return;
    }
    Message.success('修改成功');
    fetchTreeData();
  };

  const deleteNode = async (key) => {
    const { error } = await deleteTestCaseNode({
      path: {
        id: key,
      },
    });
    if (error) {
      Message.error('删除失败');
      return;
    }
    Message.success('删除成功');
    fetchTreeData();
  };

  const handleMenuClick = (key, node) => {
    setCurrentNode(node);
    if (key === 'add') {
      setModalMode('add');
      form.setFieldValue('name', '');
      setModalVisible(true);
    } else if (key === 'edit') {
      setModalMode('edit');
      form.setFieldValue('name', node.dataRef.title);
      setModalVisible(true);
    } else if (key === 'delete') {
      Modal.confirm({
        title: '确认删除该节点吗？',
        content: `您将要删除节点: ${node.dataRef.title}`,
        onOk: async () => await deleteNode(node.dataRef.key),
      });
    }
  };

  const handleModalOk = async () => {
    try {
      await form.validate();
      const values = form.getFieldsValue();
      if (modalMode === 'add-root-node') {
        await addRootNode(values.name);
      } else if (modalMode === 'add') {
        await addNode(currentNode.dataRef.key, values.name);
      } else if (modalMode === 'edit') {
        await updateNode(currentNode.dataRef.key, values.name);
      } else {
        Message.error('操作失败');
      }
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      // error will be displayed in addNode or updateNode
    }
  };

  const renderExtra = (node: NodeProps) => {
    const droplist = (
      <Menu onClickMenuItem={(key) => handleMenuClick(key, node)}>
        <Menu.Item key="add">
          <IconPlus />
          {' 新增'}
        </Menu.Item>
        <Menu.Item key="edit">
          <IconEdit />
          {' 修改'}
        </Menu.Item>
        <Menu.Item key="delete">
          <IconDelete />
          {' 删除'}
        </Menu.Item>
      </Menu>
    );

    return (
      <div className={styles['search-tree-row-div']}>
        <Badge
          className={styles['search-tree-row-badge']}
          maxCount={999}
          dotStyle={{
            fontSize: 10,
            background: 'var(--color-fill-2)',
            color: '#86909C',
          }}
          count={node.dataRef.case_count}
        />
        <Dropdown droplist={droplist} trigger="click" position="bl">
          <IconMore
            style={{
              fontSize: 14,
              color: '#3370ff',
              cursor: 'pointer',
            }}
          />
        </Dropdown>
      </div>
    );
  };

  const expandAll = (treeData, expandKeys = []) => {
    const _keys = treeUtils.expandAll(treeData, expandKeys);
    setExpandedKeys(_keys);
  };

  const collapseAll = () => {
    setExpandedKeys([]);
  };

  const onDragEvent = (
    props: NodeProps,
    e: React.DragEvent<HTMLDivElement>
  ) => {
    e.preventDefault();
    const recordID = e.dataTransfer.getData('text/plain');
    getTestCase({
      path: {
        id: Number(recordID),
      },
    })
      .then(({ data: caseInfo, error: getCaseError }) => {
        if (getCaseError) {
          console.error('Failed to get case:', getCaseError);
          Message.error('获取用例信息失败');
          return;
        }
        return caseInfo;
      })
      .then((caseInfo) => {
        return updateTestCase({
          path: {
            id: Number(recordID),
          },
          body: {
            ...caseInfo,
            node_id: Number(props.dataRef.key),
          },
        });
      })
      .then(({ error }) => {
        if (error) {
          console.error('Failed to update case:', error);
          Message.error('更新用例信息失败');
          return;
        }
        Message.success('更新成功');
        fetchTreeData();
        dispatch({
          type: 'update-case',
        });
      })
      .catch((error) => {
        console.error('Failed to update case:', error);
        Message.error('更新用例信息失败');
      });
  };

  const DragNode = (props: NodeProps) => {
    return <div onDrop={(e) => onDragEvent(props, e)}>{props.title}</div>;
  };

  const HighlightNode = (props: NodeProps) => {
    if (inputValue) {
      const index = props.title
        .toString()
        .toLowerCase()
        .indexOf(inputValue.toLowerCase());
      if (index === -1) return DragNode(props);
      const prefix = props.title.toString().slice(0, index);
      const suffix = props.title.toString().slice(index + inputValue.length);
      return (
        <div onDrop={(e) => onDragEvent(props, e)}>
          {prefix}
          <span style={{ color: 'var(--color-primary-light-4)' }}>
            {props.title.toString().slice(index, inputValue.length)}
          </span>
          {suffix}{' '}
        </div>
      );
    }
    return DragNode(props);
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '97%',
      }}
    >
      <Input.Search
        size="mini"
        allowClear
        className={styles['input-search']}
        onChange={setInputValue}
        placeholder="模糊查找节点"
      />
      <div style={{ width: '100%' }}>
        <Row className={styles['root-node-grid']}>
          <Col
            className={styles['all-cases-col']}
            flex="auto"
            push={0}
            onClick={() => onCheckedKeysChange([], null)}
          >
            <IconFolderAdd style={{ fontSize: 16 }} />
            全部用例
          </Col>
          <Col className={styles['buttons-col']} flex="30px">
            <Space style={{ margin: 0 }}>
              <Tooltip
                content={expandedKeys.length ? '收起所有节点' : '展开所有节点'}
              >
                <Button
                  size="mini"
                  type="outline"
                  shape="circle"
                  style={{ paddingRight: 5, paddingLeft: 5, paddingTop: 3 }}
                  icon={expandedKeys.length ? <IconShrink /> : <IconExpand />}
                  onClick={() =>
                    expandedKeys.length ? collapseAll() : expandAll(treeData)
                  }
                />
              </Tooltip>

              {props.readonly ? null : (
                <Tooltip content="新增根节点">
                  <Button
                    size="mini"
                    type="primary"
                    style={{ paddingRight: 5, paddingLeft: 5, paddingTop: 3 }}
                    shape="circle"
                    onClick={handleAddRootNode}
                    icon={<IconPlus />}
                  />
                </Tooltip>
              )}
            </Space>{' '}
          </Col>
        </Row>
      </div>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Tree
          size="mini"
          blockNode
          showLine={true}
          expandedKeys={expandedKeys}
          onExpand={(keys) => setExpandedKeys(keys)}
          onSelect={(selectedKeys, { node }) =>
            onCheckedKeysChange(selectedKeys, node)
          }
          renderExtra={props.renderExtra ? props.renderExtra : props.readonly ? null : renderExtra}
          renderTitle={(props: NodeProps) => {
            if (inputValue) {
              return HighlightNode(props);
            } else {
              return DragNode(props);
            }
          }}
        >
          {generatorTreeNodes(treeData)}
        </Tree>
      </div>

      <Modal
        title={modalMode === 'add-root-node' ? '新增根节点' : '新增节点'}
        visible={modalVisible}
        onOk={handleModalOk}
        onCancel={() => {
          setModalMode('');
          setCurrentNode(null);
          setModalVisible(false);
          form.resetFields();
        }}
        autoFocus={false}
        focusLock={true}
      >
        <Form form={form}>
          <Form.Item
            label="节点名称"
            field="name"
            rules={[{ required: true, message: '请输入节点名称' }]}
          >
            <Input placeholder="请输入节点名称" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default SearchTree;
