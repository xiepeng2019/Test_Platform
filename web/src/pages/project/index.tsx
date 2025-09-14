import React, { useState, useEffect, useMemo } from 'react';
import {
  Table,
  Card,
  PaginationProps,
  Button,
  Space,
  Typography,
  Modal,
  Message,
} from '@arco-design/web-react';
import PermissionWrapper from '@/components/PermissionWrapper';
import { IconPlus } from '@arco-design/web-react/icon';
import useLocale from '@/utils/useLocale';
import SearchForm from './SearchForm';
import ModalForm from './ModalForm';
import locale from './locale';
import styles from './style/index.module.less';
import { getColumns } from './constants';
import { deleteProject, listProject, Project } from '@/client';

const { Title } = Typography;

function ProjectPage() {
  const t = useLocale(locale);
  const [visible, setVisible] = useState(false);

  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [readOnly, setReadOnly] = useState(false);

  const tableCallback = async (record, type) => {
    if (type === 'detail') {
      setCurrentProject(record);
      setReadOnly(true);
      setVisible(true);
      return;
    }
    if (type === 'edit') {
      setCurrentProject(record);
      setReadOnly(false);
      setVisible(true);
      return;
    }
    if (type === 'delete') {
      Modal.confirm({
        title: '确认删除',
        content: `您确定要删除项目 [${record.name}] 吗？`,
        onOk: async () => {
          const { error } = await deleteProject({
            path: { id: record.id },
            throwOnError: false
          })
          if (error === undefined) {
            Message.success('删除成功');
            fetchData();
          } else {
            Message.error('删除失败');
          }
        },
      });
    }
  };

  const columns = useMemo(() => getColumns(t, tableCallback), [t]);

  const [data, setData] = useState<Project[]>([]);
  const [pagination, setPatination] = useState<PaginationProps>({
    sizeCanChange: true,
    showTotal: true,
    pageSize: 10,
    current: 1,
    pageSizeChangeResetCurrent: true,
  });
  const [loading, setLoading] = useState(true);
  const [formParams, setFormParams] = useState({});

  useEffect(() => {
    fetchData();
  }, [pagination.current, pagination.pageSize, JSON.stringify(formParams)]);

  function fetchData() {
    const { current, pageSize } = pagination;
    setLoading(true);
    console.log(formParams)
    listProject({
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
  }

  function onChangeTable({ current, pageSize }) {
    setPatination({
      ...pagination,
      current,
      pageSize,
    });
  }

  function handleSearch(params) {
    setPatination({ ...pagination, current: 1 });
    setFormParams(params);
  }

  return (
    <Card>
      <Title heading={6}>{t['menu.project']}</Title>
      <SearchForm onSearch={handleSearch} />
      <PermissionWrapper
        requiredPermissions={[{ resource: 'menu.project', actions: ['write'] }]}
      >
        <div className={styles['button-group']}>
          <Space>
            <Button
              size='mini'
              type="primary"
              icon={<IconPlus />}
              onClick={() => {
                setCurrentProject(null);
                setReadOnly(false);
                setVisible(true);
              }}
            >
              {t['project.operations.create']}
            </Button>
          </Space>
        </div>
      </PermissionWrapper>
      <Table<Project>
        rowKey="id"
        size="mini"
        loading={loading}
        onChange={onChangeTable}
        pagination={pagination}
        columns={columns}
        data={data}
        scroll={{
          x: 2200,
          y: 550,
        }}
      />
      <ModalForm
        project={currentProject}
        visible={visible}
        readOnly={readOnly}
        onCancel={() => {
          setVisible(false);
          setReadOnly(false);
          setCurrentProject(null);
        }}
        onOk={() => {
          setVisible(false);
          setReadOnly(false);
          setCurrentProject(null);
          fetchData();
        }}
      />
    </Card>
  );
}

export default ProjectPage;
