import { useState } from "react";
import Header from "@/components/shared/Header";
import FingerprintClassifierView from "@/views/FingerprintClassifierView";
import BloodTypeClassifierView from "@/views/BloodTypeClassifierView";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Fingerprint, Droplet } from "lucide-react";

const Index = () => {
  const [activeTool, setActiveTool] = useState<'fingerprint' | 'bloodtype'>('fingerprint');

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <Tabs value={activeTool} onValueChange={(value) => setActiveTool(value as 'fingerprint' | 'bloodtype')}>
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="fingerprint" className="flex items-center gap-2">
              <Fingerprint className="w-4 h-4" />
              Fingerprint
            </TabsTrigger>
            <TabsTrigger value="bloodtype" className="flex items-center gap-2">
              <Droplet className="w-4 h-4" />
              Blood Type
            </TabsTrigger>
          </TabsList>

          <TabsContent value="fingerprint">
            <FingerprintClassifierView />
          </TabsContent>

          <TabsContent value="bloodtype">
            <BloodTypeClassifierView />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
