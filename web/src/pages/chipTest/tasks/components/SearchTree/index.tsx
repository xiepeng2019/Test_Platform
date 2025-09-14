import React, { useState, useEffect } from 'react';
import {
  Input,
  Message,
  Button,
  Space,
  Tooltip,
  Tree,
} from '@arco-design/web-react';
import {
  IconExpand,
  IconShrink,
  IconFolderAdd,
} from '@arco-design/web-react/icon';
import styles from '@/pages/chipTest/cases/style/index.module.less';
import useLocale from '@/utils/useLocale';
import locale from '@/pages/chipTest/cases/locale';
import {
  NodeInstance,
  NodeProps,
} from '@arco-design/web-react/es/Tree/interface';
import {
  getTestTaskTree,
  listTestCaseNodeTree,
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
  taskId: number;
}

function SearchTree(props: SearchTreeProps) {
  const onCheckedKeysChange = props.onCheckedKeysChange;
  const [treeData, setTreeData] = useState<NodeProps[]>([]);
  const [originalTreeData, setOriginalTreeData] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [expandedKeys, setExpandedKeys] = useState([]);
  const t = useLocale(locale);
  const treeUtils = new TreeUtils();

  useEffect(() => {
    fetchTreeData();
  }, [props.taskId]);

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
      const { data, error } = props.taskId ? await getTestTaskTree({path: {id: props.taskId}}) : await listTestCaseNodeTree()
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

  const expandAll = (treeData, expandKeys = []) => {
    const _keys = treeUtils.expandAll(treeData, expandKeys);
    setExpandedKeys(_keys);
  };

  const collapseAll = () => {
    setExpandedKeys([]);
  };

  const HighlightNode = (props: NodeProps) => {
    if (inputValue) {
      const index = props.title
        .toString()
        .toLowerCase()
        .indexOf(inputValue.toLowerCase());
      if (index === -1) return <div>{props.title}</div>;
      const prefix = props.title.toString().slice(0, index);
      const suffix = props.title.toString().slice(index + inputValue.length);
      return (
        <div>
          {prefix}
          <span style={{ color: 'var(--color-primary-light-4)' }}>
            {props.title.toString().slice(index, inputValue.length)}
          </span>
          {suffix}{' '}
        </div>
      );
    }
    return <div>{props.title}</div>;
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
            <IconFolderAdd style={{ fontSize: 18 }} />
            全部用例
          </Col>
          <Col className={styles['buttons-col']} flex="30px">
            <Space>
              <Tooltip
                content={expandedKeys.length ? '收起所有节点' : '展开所有节点'}
              >
                <Button
                  size="mini"
                  type="outline"
                  shape="round"
                  style={{ paddingRight: 5, paddingLeft: 5, paddingTop: 3 }}
                  icon={expandedKeys.length ? <IconShrink /> : <IconExpand />}
                  onClick={() =>
                    expandedKeys.length ? collapseAll() : expandAll(treeData)
                  }
                />
              </Tooltip>
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
          renderExtra={props.renderExtra}
          renderTitle={(props: NodeProps) => {
              return HighlightNode(props);
          }}
        >
          {generatorTreeNodes(treeData)}
        </Tree>
      </div>
    </div>
  );
}

export default SearchTree;
