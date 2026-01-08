import { Panel, Group, Separator } from 'react-resizable-panels';

export function TestPanels() {
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ height: '50px', background: '#333', color: '#fff', display: 'flex', alignItems: 'center', paddingLeft: '20px' }}>
        Test Header
      </div>
      <div style={{ flex: 1 }}>
        {/* @ts-expect-error - react-resizable-panels Group 类型定义问题 */}
        <Group direction="horizontal">
          <Panel defaultSize={25} minSize={15}>
            <div style={{ height: '100%', background: '#2a2a2a', padding: '20px', color: '#fff' }}>
              Left Panel
            </div>
          </Panel>
          <Separator />
          <Panel defaultSize={50} minSize={30}>
            <div style={{ height: '100%', background: '#1a1a1a', padding: '20px', color: '#fff' }}>
              Middle Panel
            </div>
          </Panel>
          <Separator />
          <Panel defaultSize={25} minSize={15}>
            <div style={{ height: '100%', background: '#2a2a2a', padding: '20px', color: '#fff' }}>
              Right Panel
            </div>
          </Panel>
        </Group>
      </div>
    </div>
  );
}
