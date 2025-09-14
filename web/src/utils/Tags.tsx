import React from 'react';
import {
  Tag,
} from '@arco-design/web-react';
import { CaseRecordStatus, TaskRecordStatus } from '@/client';


function getColorByTaskStatus(status: TaskRecordStatus) {
  switch (status) {
    case TaskRecordStatus.PASSED:
      return 'green';
    case TaskRecordStatus.FAILED:
      return 'red';
    case TaskRecordStatus.RUNNING:
      return 'blue';
    case TaskRecordStatus.CANCELED:
      return 'orange';
    case TaskRecordStatus.ERROR:
      return 'red';
    case TaskRecordStatus.CREATED:
      return 'orange';
    default:
      return 'gray';
  }
}

function getColorByCaseStatus(status: CaseRecordStatus) {
  switch (status) {
    case CaseRecordStatus.PASSED:
      return 'green';
    case CaseRecordStatus.FAILED:
      return 'red';
    default:
      return 'gray';
  }
}

export function getTaskStatusLabel(status: TaskRecordStatus) {
  const color = getColorByTaskStatus(status);
  return status && <Tag color={color}>{status?.toUpperCase()}</Tag>;
}

export function getCaseStatusLabel(status: CaseRecordStatus) {
  const color = getColorByCaseStatus(status);
  return status && <Tag color={color}>{status?.toUpperCase()}</Tag>;
}