import { useEffect, useMemo, useState } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type NodeProps,
  type Node,
  type Edge,
  type ReactFlowInstance,
} from "@xyflow/react";
import { FlaskConical, Sun, Zap } from "lucide-react";
import "@xyflow/react/dist/style.css";
import { categories, type Molecule, type Reaction } from "./types";

type MoleculeNode = Node<{ molecule: Molecule; active: boolean }, "molecule">;
type ReactionNode = Node<{ reaction: Reaction; active: boolean }, "reaction">;

function MoleculeCard({ data }: NodeProps<MoleculeNode>) {
  return (
    <div className={`molecule-node ${data.active ? "active" : ""}`}>
      <Handle type="target" position={Position.Left} />
      <div className="node-kicker">
        <span className="small-dot" />
        MOLECULE {data.molecule.is_demo && <span>DEMO</span>}
      </div>
      <img
        src={`/api/molecules/${data.molecule.id}/svg`}
        alt={`${data.molecule.name} structure`}
        draggable={false}
      />
      <strong>{data.molecule.name}</strong>
      <div className="node-formula">
        {data.molecule.formula}
        <span>{data.molecule.molecular_weight} g/mol</span>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
function ReactionCard({ data }: NodeProps<ReactionNode>) {
  const category = categories[data.reaction.category];
  const Icon =
    data.reaction.category === "photochemical"
      ? Sun
      : data.reaction.category === "electrochemical"
        ? Zap
        : FlaskConical;
  return (
    <div
      className={`reaction-node ${data.active ? "active" : ""}`}
      style={{ "--reaction-color": category.color } as React.CSSProperties}
    >
      <Handle type="target" position={Position.Left} />
      <Icon size={18} />
      <span>{category.short}</span>
      <strong>{data.reaction.name}</strong>
      <small>
        {data.reaction.is_demo
          ? "Demo connection"
          : data.reaction.status === "reviewed"
            ? "Record reviewed"
            : "Draft"}
      </small>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
const nodeTypes = { molecule: MoleculeCard, reaction: ReactionCard };

export function Graph({
  molecules,
  reactions,
  selected,
  onSelect,
}: {
  molecules: Molecule[];
  reactions: Reaction[];
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const graph = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const level = new Map(molecules.map((m) => [m.id, 0]));
    const cyclic = new Set<string>();
    for (let i = 0; i < Math.min(molecules.length, 12); i++) {
      let changed = false;
      for (const r of reactions) {
        const next = Math.min(
          12,
          Math.max(...r.reactants.map((id) => level.get(id) || 0)) + 2,
        );
        for (const id of r.products)
          if ((level.get(id) || 0) < next) {
            level.set(id, next);
            changed = true;
            if (i === Math.min(molecules.length, 12) - 1) cyclic.add(id);
          }
      }
      if (!changed) break;
    }
    // Cycles are still connected by edges; constrain their display columns.
    for (const id of cyclic) level.set(id, 2);
    const columns = new Map<number, number>();
    const place = (column: number, height: number) => {
      const y = columns.get(column) || 0;
      columns.set(column, y + height);
      return { x: column * 180, y };
    };
    for (const molecule of molecules)
      nodes.push({
        id: molecule.id,
        type: "molecule",
        position: place(level.get(molecule.id) || 0, 225),
        data: { molecule, active: selected === molecule.id },
      });
    for (const reaction of reactions) {
      const column = Math.min(
        11,
        Math.max(...reaction.reactants.map((id) => level.get(id) || 0)) + 1,
      );
      nodes.push({
        id: reaction.id,
        type: "reaction",
        position: place(column, 225),
        data: { reaction, active: selected === reaction.id },
      });
      for (const id of reaction.reactants)
        edges.push({
          id: `${id}-${reaction.id}`,
          source: id,
          target: reaction.id,
          type: "smoothstep",
          style: {
            stroke: categories[reaction.category].color,
            strokeWidth: 1.5,
            opacity: 0.65,
          },
        });
      for (const id of reaction.products)
        edges.push({
          id: `${reaction.id}-${id}`,
          source: reaction.id,
          target: id,
          type: "smoothstep",
          style: {
            stroke: categories[reaction.category].color,
            strokeWidth: 1.5,
            opacity: 0.65,
          },
          markerEnd: {
            type: "arrowclosed",
            color: categories[reaction.category].color,
          } as Edge["markerEnd"],
        });
    }
    return { nodes, edges };
  }, [molecules, reactions, selected]);
  const [nodes, setNodes, onNodesChange] = useNodesState(graph.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(graph.edges);
  const [instance, setInstance] = useState<ReactFlowInstance | null>(null);
  const graphKey =
    molecules.map((m) => m.id).join(",") + reactions.map((r) => r.id).join(",");
  useEffect(() => {
    setNodes(graph.nodes);
    setEdges(graph.edges);
  }, [graph, setNodes, setEdges]);
  useEffect(() => {
    if (!instance) return;
    const timer = setTimeout(() => {
      void instance.fitView({ padding: 0.18, duration: 180 });
    }, 60);
    return () => clearTimeout(timer);
  }, [graphKey, instance]);
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onInit={setInstance}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={(_, node) => onSelect(node.id)}
      fitView
      fitViewOptions={{ padding: 0.18 }}
      minZoom={0.25}
      maxZoom={1.5}
      nodesConnectable={false}
      proOptions={{ hideAttribution: true }}
    >
      <Background
        color="#354038"
        gap={24}
        size={1}
        variant={BackgroundVariant.Dots}
      />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
