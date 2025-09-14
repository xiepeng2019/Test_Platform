import React, { useCallback, useState } from 'react';
import CaseTable from './table';
import styles from './style/index.module.less';
import SearchTree from './search-tree';
import { ResizeBox } from '@arco-design/web-react';


function CasePage() {
  const [selectedTreeNode, setSelectedTreeNode] = useState<string[]>([]);
  const onCheckedKeysChange = useCallback((checkedKeys: string[]) => {
    setSelectedTreeNode(checkedKeys);
  }, []);

  return (
    <div className={styles['test-plan-card']}>
      <ResizeBox.SplitGroup
        className={styles['operations']}
        direction={'horizontal'}
        panes={[
          {
            content: (
              <SearchTree
                key={'search-tree'}
                onCheckedKeysChange={onCheckedKeysChange}
              />
            ),
            size: 0.2,
          },
          {
            content: (
              <CaseTable key={'case-table'} selectedTreeNode={selectedTreeNode} />
            ),
            min: '600px',
          },
        ]}
      />
    </div>
  );
}
export default CasePage;
