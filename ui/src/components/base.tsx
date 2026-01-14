import { useState, type ChangeEvent } from "react";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { StreamEvents } from "@/components/runWorkflow";

function BaseComponent() {
  const [workflowName, setWorkflowName] = useState<string | null>(null);
  const [fileBytes, setFileBytes] = useState<Uint8Array | null>(null);

  const handleWorkflowChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setWorkflowName(value === "" ? null : value);
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const arrayBuffer = await file.arrayBuffer();
      const bytes = new Uint8Array(arrayBuffer);
      setFileBytes(bytes);
    } else {
      setFileBytes(null);
    }
  };

  return (
    <div className="p-10 space-y-6">
      <div className="grid w-full max-w-sm items-center gap-3">
        <Label htmlFor="workflow">Select Workflow</Label>
        <NativeSelect id="workflow" onChange={handleWorkflowChange}>
          <NativeSelectOption value="">Select a File Type</NativeSelectOption>
          <NativeSelectOption value="sheets">Excel Sheet</NativeSelectOption>
          <NativeSelectOption value="presentations">
            PDF Presentation
          </NativeSelectOption>
        </NativeSelect>
      </div>

      <div className="grid w-full max-w-sm items-center gap-3">
        <Label htmlFor="uploadedFile">Upload a File</Label>
        <Input
          id="uploadedFile"
          type="file"
          onChange={handleFileChange}
          accept={workflowName === "sheets" ? ".xlsx,.xls" : ".pdf"}
        />
      </div>

      {workflowName && fileBytes && (
        <div className="mt-10 border p-4 rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">
            Running <strong>{workflowName}</strong>
          </p>
          <StreamEvents
            workflowName={workflowName}
            fileInput={fileBytes}
            fileExtension={workflowName === "sheets" ? ".xlsx" : ".pdf"}
          />
        </div>
      )}
    </div>
  );
}

export default BaseComponent;
