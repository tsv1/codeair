import { useMemo, type CSSProperties } from 'react';
import Convert from 'ansi-to-html';

interface AnsiOutputProps {
  content: string;
  maxHeight?: string;
  backgroundColor?: string;
  border?: string;
  preStyle?: CSSProperties;
  containerStyle?: CSSProperties;
}

export function AnsiOutput({
  content,
  maxHeight = '400px',
  backgroundColor = '#f5f5f5',
  border,
  preStyle = {},
  containerStyle = {}
}: AnsiOutputProps) {
  const ansiConverter = useMemo(() => new Convert({
    fg: '#000',
    bg: '#FFF',
    newline: true,
    escapeXML: true
  }), []);

  const convertedHtml = useMemo(() => {
    return ansiConverter.toHtml(content);
  }, [ansiConverter, content]);

  return (
    <div
      style={{
        maxHeight,
        overflow: 'auto',
        backgroundColor,
        padding: '1rem',
        borderRadius: '4px',
        border,
        ...containerStyle
      }}
    >
      <pre
        style={{
          margin: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          ...preStyle
        }}
        dangerouslySetInnerHTML={{ __html: convertedHtml }}
      />
    </div>
  );
}
