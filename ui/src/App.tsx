import "./App.css";
import { ApiProvider } from "@llamaindex/ui";
import BaseComponent from "@/components/base";
import { clients } from "@/lib/clients";

function App() {
  return (
    <div>
      <ApiProvider clients={clients}>
        <BaseComponent />
      </ApiProvider>
    </div>
  );
}

export default App;
