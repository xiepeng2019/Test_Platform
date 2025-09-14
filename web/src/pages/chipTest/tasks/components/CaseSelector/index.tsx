import React, { useCallback, useState } from 'react';
import styles from '@/pages/chipTest/cases/style/index.module.less';
import { ResizeBox, Tag } from '@arco-design/web-react';
import SearchTree from '../SearchTree';
import { NodeProps } from '@arco-design/web-react/es/Cascader';
import { TestCase } from '@/client';
import CaseTable from '../CaseSelectorTable';


export interface CaseSelectorProps {
  selectedRowKeys: (string | number)[];
  onSelectedRowKeysChange: (selectedRowKeys: (string | number)[]) => void;
  taskId?: number;
  readonly: boolean;
}


function CaseSelector(props: CaseSelectorProps) {
  const [selectedTreeNode, setSelectedTreeNode] = useState<number[]>([]);
  const renderExtra = useCallback((node: NodeProps<TestCase>) => {
    const total = node.dataRef.case_count || 0;
    const selected = node.dataRef.selected_case_count || 0;
    const isAllSelected = selected > 0 && selected === total;
    const isNoneSelected = selected === 0;
    const selectedColor = isAllSelected
      ? 'rgba(22,93,255, 1)' // greenish bg
      : isNoneSelected
      ? 'rgba(144,152,164, 1)' // neutral bg
      : 'rgba(0,180,42, 1)'; // bluish bg
    const backgroundColor = isAllSelected
      ? 'rgba(22,93,255, 0.2)'
      : isNoneSelected
      ? 'rgba(144,152,164, 0.2)'
      : 'rgba(0,180,42, 0.2)';
  
    return (
      <div className={styles['search-tree-row-div']}>
        <Tag
          size="small"
          style={{
            backgroundColor: backgroundColor,
            border: 'none',
            padding: '0 6px',
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: 10,
            borderRadius: 12,
          }}
        >
          <span style={{ color: selectedColor }}>{selected}</span>
          <span style={{ color: selectedColor }}>{' / '}</span>
          <span style={{ color: selectedColor }}>{total}</span>
        </Tag>
      </div>
    );
  }, []);
  const onCheckedKeysChange = useCallback((checkedKeys: number[]) => {
    setSelectedTreeNode(checkedKeys);
  }, []);
  return (
    <div className={styles['test-plan-card']} style={{ height: '70vh' }}>
      <ResizeBox.SplitGroup
        className={styles['operations']}
        direction={'horizontal'}
        panes={[
          {
            content: (
              <SearchTree
                renderExtra={renderExtra}
                readonly
                key={'search-tree'}
                onCheckedKeysChange={onCheckedKeysChange}
                taskId={props.taskId}
              />
            ),
            size: 0.25,
          },
          {
            content: (
              <CaseTable
                selectedTreeNode={selectedTreeNode}
                tableScroll={{ x: 600 }}
                selectedRowKeys={props.selectedRowKeys}
                setSelectedRowKeys={(selectedRowKeys) => {
                  props.onSelectedRowKeysChange(selectedRowKeys);
                }}
                readonly={props.readonly}
              />
            ),
            min: '500px',
          },
        ]}
      />
    </div>
  );
}
export default CaseSelector;
