import { useEffect, useState } from "react";
import {
  useWorkflow,
  useHandler,
  WorkflowEvent,
  isStopEvent,
} from "@llamaindex/ui";
import {
  Play,
  Loader2,
  CheckCircle2,
  Activity,
  ChevronRight,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

export interface StreamEventsProps {
  workflowName: string;
  fileInput: Uint8Array;
  fileExtension: string;
}

export function StreamEvents({
  workflowName,
  fileInput,
  fileExtension,
}: StreamEventsProps) {
  const workflow = useWorkflow(workflowName);
  const [handlerId, setHandlerId] = useState<string | null>(null);
  const handler = useHandler(handlerId);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);

  function uint8ArrayToBase64(bytes: Uint8Array): string {
    let binary = "";
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  async function start() {
    setEvents([]);
    const h = await workflow.createHandler({
      file_input: uint8ArrayToBase64(fileInput),
      file_extension: fileExtension,
      is_source_content: true,
    });
    setHandlerId(h.handler_id);
  }

  useEffect(() => {
    if (!handlerId) return;
    const sub = handler.subscribeToEvents({
      onData: (event) => setEvents((prev) => [...prev, event]),
    });
    return () => sub.unsubscribe();
  }, [handler, handlerId]);

  const stop = events.find(isStopEvent);
  const isRunning = handlerId && !stop;

  return (
    <Card className="w-full max-w-2xl mx-auto border-t-4 border-t-primary shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="space-y-1">
          <CardTitle className="text-xl flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Workflow Stream
          </CardTitle>
          <CardDescription>{workflowName}</CardDescription>
        </div>
        <Button onClick={start} size="sm" className="gap-2">
          {isRunning ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          {isRunning ? "Running..." : "Start & Stream"}
        </Button>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Status Section */}
        {handlerId && (
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Status:</span>
            <Badge
              variant={stop ? "default" : "secondary"}
              className="capitalize"
            >
              {stop ? "Completed" : handler.state.status}
            </Badge>
          </div>
        )}

        {/* Event Logs / Terminal */}
        <div className="rounded-lg bg-slate-950 p-4 text-slate-50 font-mono text-xs">
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-800 text-slate-400">
            <Terminal className="h-3 w-3" />
            <span>Event Logs</span>
          </div>
          <ScrollArea className="h-48 w-full">
            {events.length === 0 ? (
              <p className="text-slate-500 italic">
                No events received yet. Press start to begin.
              </p>
            ) : (
              <div className="space-y-1">
                {events.map((event, idx) => (
                  <div key={idx} className="flex gap-2">
                    <ChevronRight className="h-3 w-3 mt-0.5 text-blue-400 shrink-0" />
                    <span className="break-all">
                      {typeof event === "string"
                        ? event
                        : JSON.stringify(event)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Final Results View */}
        {stop && (
          <div className="mt-4 p-4 rounded-md bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900">
            <div className="flex items-center gap-2 text-green-700 dark:text-green-400 font-semibold mb-2">
              <CheckCircle2 className="h-5 w-5" />
              Workflow Finished
            </div>
            <pre className="text-xs bg-white dark:bg-black/40 p-3 rounded border border-green-200 dark:border-green-900 overflow-auto max-h-40">
              {JSON.stringify(stop.data, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>

      <CardFooter className="text-xs text-muted-foreground border-t bg-muted/30 pt-3">
        {events.length > 0 && <p>{events.length} total events processed</p>}
      </CardFooter>
    </Card>
  );
}
