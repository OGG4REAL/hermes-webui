import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  primitiveName: string;
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

/**
 * Per ADR-010: a single Layer 0 primitive crashing must not bring down the
 * entire React tree. Wrap each rendered primitive in this boundary so that
 * a faulty MetricCard / chart / table only shows a fallback in its own slot
 * while the surrounding surfaces continue to render.
 *
 * Defensive coding inside each primitive is the first line of defense; this
 * boundary is the safety net for cases we did not anticipate.
 */
export class PrimitiveErrorBoundary extends Component<Props, State> {
  constructor(p: Props) {
    super(p);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(err: unknown): State {
    return {
      hasError: true,
      message: err instanceof Error ? err.message : String(err),
    };
  }

  componentDidCatch(err: Error, info: ErrorInfo): void {
    // eslint-disable-next-line no-console
    console.warn(
      `[PrimitiveErrorBoundary] ${this.props.primitiveName} crashed:`,
      err,
      info.componentStack,
    );
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={fallbackStyle}>
          <div style={titleStyle}>{this.props.primitiveName} 渲染失败</div>
          <div style={msgStyle}>{this.state.message}</div>
        </div>
      );
    }
    return this.props.children;
  }
}

const fallbackStyle: React.CSSProperties = {
  border: "1px dashed #fda29b",
  background: "#fef3f2",
  borderRadius: 8,
  padding: "12px 14px",
};

const titleStyle: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: "#b42318",
  marginBottom: 4,
};

const msgStyle: React.CSSProperties = {
  fontSize: 12,
  color: "#912018",
  fontFamily: "monospace",
  wordBreak: "break-word",
};
