export class TreeUtils {
  public expandAll = (treeData, expandKeys = []) => {
    for (let i = 0; i < treeData.length; i++) {
      expandKeys.push(treeData[i].key);
      if (treeData[i].children) {
        this.expandAll(treeData[i].children, expandKeys);
      }
    }
    return expandKeys;
  };

  public searchData(inputValue: string, treeData) {
    const loop = (data) => {
      const result = [];
      data.forEach((item) => {
        if (item.title.toLowerCase().indexOf(inputValue.toLowerCase()) > -1) {
          result.push({ ...item });
        } else if (item.children) {
          const filterData = loop(item.children);

          if (filterData.length) {
            result.push({ ...item, children: filterData });
          }
        }
      });
      return result;
    };
    return loop(treeData);
  }
}