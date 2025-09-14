import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Table,
  Modal,
  Message,
  PaginationProps,
  Space,
  Button,
} from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import styles from './style/index.module.less';
import { getColumns } from './constants';
import { GlobalState } from '@/store';
import SearchForm from './form';
import AddForm from './modal-form';
import PermissionWrapper from '@/components/PermissionWrapper';
import {
  IconDragDotVertical,
  IconPlus,
  IconUpload,
} from '@arco-design/web-react/icon';
import { SortableHandle } from 'react-sortable-hoc';
import {
  deleteTestCase,
  listTestCase,
  TestCase,
  updateTestCase,
} from '@/client';
import UpdateNodesForm from './update-nodes-form';
import UploadModalForm from './upload-modal';

export interface CaseTableProps {
  selectedTreeNode: string[];
  tableScroll?: {
    x?: number;
    y?: number;
  };
}

function CaseTable(props: CaseTableProps) {
  const t = useLocale(locale);
  const dispatch = useDispatch();
  const { selectedTreeNode } = props;
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [visible, setVisible] = useState(false);
  const [uploadVisible, setUploadVisible] = useState(false);
  const [currentCase, setCurrentCase] = useState<TestCase | null>(null);
  const [readOnly, setReadOnly] = useState(false);

  const [data, setData] = useState<TestCase[]>([]);
  const [pagination, setPatination] = useState<PaginationProps>({
    sizeCanChange: true,
    showTotal: true,
    pageSize: 15,
    current: 1,
    pageSizeChangeResetCurrent: true,
  });
  const [loading, setLoading] = useState(true);
  const [formParams, setFormParams] = useState({});
  const [updateNodeVisible, setUpdateNodeVisible] = useState(false);

  const tableCallback = async (record: TestCase, type: string) => {
    if (type === 'detail') {
      setCurrentCase(record);
      setReadOnly(true);
      setVisible(true);
      return;
    } else if (type === 'edit') {
      setCurrentCase(record);
      setReadOnly(false);
      setVisible(true);
      return;
    } else if (type === 'delete') {
      Modal.confirm({
        title: t['case.operations.delete.title'],
        content:
          t['case.operations.delete.content'] + '[' + record.name + ']' + '?',
        onOk: async () => {
          deleteTestCase({ path: { id: record.id } })
            .then(() => {
              Message.success(t['case.operations.delete.ok']);
              fetchData();
            })
            .catch(() => {
              Message.error(t['case.operations.delete.fail']);
            });
        },
      });
    }
  };

  const columns = useMemo(() => getColumns(t, tableCallback), [t]);
  const caseUpdate = useSelector((state: GlobalState) => state.caseUpdate);

  const { current, pageSize } = pagination;
  const fetchData = useCallback(() => {
    setLoading(true);
    console.log('formParams', formParams);
    listTestCase({
      query: {
        page: current,
        pageSize,
        ...formParams,
      },
    }).then((res) => {
      setData(res.data.list);
      setPatination({
        ...pagination,
        current,
        pageSize,
        total: res.data.total,
      });
      setLoading(false);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current, pageSize, formParams]);

  useEffect(() => {
    fetchData();
  }, [fetchData, caseUpdate]);

  useEffect(() => {
    if (selectedTreeNode.length > 0) {
      const newFormParams = { ...formParams, node_id: selectedTreeNode[0] };
      setFormParams(newFormParams);
      setPatination({ ...pagination, current: 1 });
    } else if (selectedTreeNode.length === 0) {
      setFormParams({ ...formParams, node_id: [] });
      setPatination({ ...pagination, current: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTreeNode]);

  function onChangeTable({ current, pageSize }) {
    setPatination({
      ...pagination,
      current,
      pageSize,
    });
  }

  function handleSearch(params: Record<string, string>) {
    setPatination({ ...pagination, current: 1 });
    setFormParams(params);
  }

  const DragHandle = SortableHandle(() => (
    <IconDragDotVertical
      style={{
        cursor: 'move',
        color: '#555',
      }}
    />
  ));

  const DraggableRow = (props) => {
    const { children, record } = props;
    return (
      <tr
        draggable
        onDragStart={(e) => {
          e.dataTransfer.setData('text/plain', record.id);
        }}
      >
        {children}
      </tr>
    );
  };

  const components = {
    header: {
      operations: ({ selectionNode }) => [
        {
          node: <th />,
          width: 40,
        },
        {
          name: 'selectionNode',
          node: selectionNode,
        },
      ],
    },
    body: {
      operations: ({ selectionNode }) => [
        {
          node: (
            <td>
              <div className="arco-table-cell">
                <DragHandle />
              </div>
            </td>
          ),
          width: 40,
        },
        {
          name: 'selectionNode',
          node: selectionNode,
        },
      ],
      row: DraggableRow,
    },
  };

  return (
    <div className={styles['table-content']}>
      <SearchForm onSearch={handleSearch} />
      <PermissionWrapper
        requiredPermissions={[{ resource: 'menu.case', actions: ['write'] }]}
      >
        <div className={styles['button-group']}>
          <Space>
            <Button
              size="mini"
              type="primary"
              icon={<IconPlus />}
              onClick={() => {
                setCurrentCase(null);
                setReadOnly(false);
                setVisible(true);
              }}
            >
              {t['case.operations.create']}
            </Button>
            <Button
              size="mini"
              type="outline"
              icon={<IconUpload />}
              onClick={() => {
                setCurrentCase(null);
                setReadOnly(false);
                setUploadVisible(true);
              }}
            >
              {t['case.operations.upload']}
            </Button>
          </Space>
        </div>
      </PermissionWrapper>
      <Table
        size="mini"
        rowKey="id"
        rowSelection={{
          type: 'checkbox',
          selectedRowKeys,
          onChange: (selectedRowKeys, selectedRows) => {
            console.log('onChange:', selectedRowKeys, selectedRows);
            setSelectedRowKeys(selectedRowKeys);
          },
          onSelect: (selected, record, selectedRows) => {
            console.log('onSelect:', selected, record, selectedRows);
          },
          checkboxProps: (record) => {
            return {
              disabled: record.id === '4',
            };
          },
        }}
        renderPagination={(paginationNode) => (
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: 10,
            }}
          >
            {selectedRowKeys.length > 0 ? (
              <Space>
                <span style={{ color: '#555', fontSize: 12 }}>
                  已选择 {selectedRowKeys.length} 条用例
                </span>
                <Button
                  type="outline"
                  shape="round"
                  status="success"
                  size="mini"
                  onClick={() => {
                    Message.warning('暂未开放');
                  }}
                >
                  导出
                </Button>
                <Button
                  type="outline"
                  shape="round"
                  status="success"
                  size="mini"
                  onClick={() => {
                    setUpdateNodeVisible(true);
                  }}
                >
                  移动到
                </Button>
                <Button
                  type="outline"
                  shape="round"
                  status="danger"
                  size="mini"
                  onClick={() => {
                    Message.warning('暂未开放');
                  }}
                >
                  删除
                </Button>
              </Space>
            ) : (
              <div></div>
            )}
            {paginationNode}
          </div>
        )}
        loading={loading}
        onChange={onChangeTable}
        pagination={pagination}
        columns={columns}
        data={data}
        components={components}
        style={{ marginLeft: 10, marginBottom: 40 }}
        tableLayoutFixed={true}
        scroll={
          props.tableScroll || {
            x: 2000,
          }
        }
      />
      <AddForm
        testCase={currentCase}
        visible={visible}
        readOnly={readOnly}
        onCancel={() => {
          setVisible(false);
          setReadOnly(false);
          setCurrentCase(null);
        }}
        onOk={() => {
          setVisible(false);
          setReadOnly(false);
          setCurrentCase(null);
          fetchData();
        }}
      />
      <UpdateNodesForm
        visible={updateNodeVisible}
        onCancel={() => {
          setUpdateNodeVisible(false);
        }}
        onOk={async (nodeID) => {
          console.log('onOk:', nodeID);
          selectedRowKeys.forEach(async (key) => {
            const { error } = await updateTestCase({
              path: {
                id: key,
              },
              body: {
                node_id: Number(nodeID),
              },
            });
            if (error) {
              Message.error('修改失败');
              return;
            }
            Message.success('修改成功');
            fetchData();
          });
          setUpdateNodeVisible(false);
          setSelectedRowKeys([]);
          fetchData();
        }}
      />
      <UploadModalForm
        visible={uploadVisible}
        onCancel={() => {
          setUploadVisible(false);
        }}
        onOk={() => {
          setUploadVisible(false);
          dispatch({ type: 'update-case' });
        }}
      />
    </div>
  );
}

export default CaseTable;
