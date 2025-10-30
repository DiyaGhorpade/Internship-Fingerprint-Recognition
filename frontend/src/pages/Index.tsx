import { useState } from "react";
import Header from "@/components/shared/Header";
import FingerprintClassifierView from "@/views/FingerprintClassifierView";
import BloodTypeClassifierView from "@/views/BloodTypeClassifierView";
import AnalyticsView from "@/views/AnalyticsView"; // ✅ add this
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Fingerprint, Droplet, BarChart3 } from "lucide-react"; // ✅ add icon

const Index = () => {
  const [activeTool, setActiveTool] = useState("fingerprint");


  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <Tabs
          value={activeTool}
          onValueChange={(value) =>
            setActiveTool(value as 'fingerprint' | 'bloodtype' | 'analytics')
          }
        >
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-3 mb-8">
            <TabsTrigger value="fingerprint" className="flex items-center gap-2">
              <Fingerprint className="w-4 h-4" />
              Fingerprint
            </TabsTrigger>

            <TabsTrigger value="bloodtype" className="flex items-center gap-2">
              <Droplet className="w-4 h-4" />
              Blood Type
            </TabsTrigger>

            {/* ✅ New Analytics Tab */}
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="fingerprint">
            <FingerprintClassifierView />
          </TabsContent>

          <TabsContent value="bloodtype">
            <BloodTypeClassifierView />
          </TabsContent>

          {/* ✅ Analytics View */}
          <TabsContent value="analytics">
            <AnalyticsView />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
