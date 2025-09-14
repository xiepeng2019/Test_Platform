import { Message, Modal } from '@arco-design/web-react';
import React, { useEffect, useState } from 'react';
import SearchTree from './search-tree';
import { NodeInstance } from '@arco-design/web-react/es/Tree/interface';

export interface UpdateNodesFormProps {
  visible: boolean;
  onCancel: () => void;
  onOk: (nodeID: string) => void;
}

const UpdateNodesForm = (props: UpdateNodesFormProps) => {
  const { visible, onCancel, onOk } = props;
  const [currentNode, setCurrentNode] = useState<NodeInstance>();

  useEffect(() => {
    setCurrentNode(null);
  }, [visible]);

  return (
    <Modal
      title={currentNode ? `批量移动到 ${currentNode.props.title}` : '批量移动'}
      visible={visible}
      onCancel={onCancel}
      onOk={() => {
        currentNode ? onOk(currentNode.key) : Message.error('请选择节点');
      }}
      mountOnEnter={false}
      unmountOnExit
    >
      <div style={{ maxHeight: '60vh', overflow: 'auto' }}>
        <SearchTree
          onCheckedKeysChange={(_, node) => {
            setCurrentNode(node);
          }}
          readonly
        />
      </div>
    </Modal>
  );
};

export default UpdateNodesForm;
