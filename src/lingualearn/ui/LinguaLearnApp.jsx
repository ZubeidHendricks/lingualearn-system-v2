import React, { useState, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Button } from '../../components/ui/button';
import { Camera, Book, Settings, Globe } from 'lucide-react';
import CameraView from './CameraView';

const LinguaLearnApp = () => {
    const [activeTab, setActiveTab] = useState('camera');
    const [currentLanguage, setCurrentLanguage] = useState('xho');
    const [userRegion, setUserRegion] = useState('Western Cape');
    const [learningMode, setLearningMode] = useState('linguist');
    const [detectedObjects, setDetectedObjects] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);

    const handleCapture = useCallback(async (frameData) => {
        setIsProcessing(true);
        try {
            // For testing, return a mock result
            return {
                success: true,
                object: {
                    name: 'Test Object',
                    local_term: 'Test Term',
                    confidence: 0.95
                }
            };
        } catch (error) {
            console.error('Object detection error:', error);
            return { success: false, error: error.message };
        } finally {
            setIsProcessing(false);
        }
    }, []);

    const handleRecordTerm = useCallback(async () => {
        try {
            // For testing, return a mock result
            return {
                success: true,
                text: 'Test recording'
            };
        } catch (error) {
            console.error('Recording error:', error);
            return { success: false, error: error.message };
        }
    }, []);

    return (
        <div className="h-screen flex flex-col bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">LinguaLearn</h1>
                    <div className="flex items-center space-x-4">
                        <select
                            value={currentLanguage}
                            onChange={(e) => setCurrentLanguage(e.target.value)}
                            className="px-3 py-2 border rounded-lg"
                        >
                            <option value="xho">isiXhosa</option>
                            <option value="zul">isiZulu</option>
                            <option value="sot">Sesotho</option>
                            <option value="afr">Afrikaans</option>
                        </select>
                        <Button
                            variant={learningMode === 'linguist' ? 'default' : 'outline'}
                            onClick={() => setLearningMode(mode => 
                                mode === 'linguist' ? 'student' : 'linguist'
                            )}
                        >
                            <Globe className="mr-2 h-4 w-4" />
                            {learningMode === 'linguist' ? 'Linguist' : 'Student'}
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="flex-1 overflow-hidden bg-gray-50">
                <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="h-full flex flex-col"
                >
                    <TabsList className="px-4 pt-4">
                        <TabsTrigger value="camera" className="flex items-center">
                            <Camera className="mr-2 h-4 w-4" />
                            Learn
                        </TabsTrigger>
                        <TabsTrigger value="dictionary" className="flex items-center">
                            <Book className="mr-2 h-4 w-4" />
                            Dictionary
                        </TabsTrigger>
                        <TabsTrigger value="settings" className="flex items-center">
                            <Settings className="mr-2 h-4 w-4" />
                            Settings
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="camera" className="flex-1 p-4 h-full">
                        <CameraView
                            onCapture={handleCapture}
                            onRecordTerm={{
                                start: handleRecordTerm,
                                stop: handleRecordTerm
                            }}
                        />
                    </TabsContent>

                    <TabsContent value="dictionary" className="flex-1 p-4">
                        <div className="h-full rounded-lg bg-white shadow-sm p-4">
                            <h2 className="text-xl font-semibold mb-4">Object Dictionary</h2>
                            {detectedObjects.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {detectedObjects.map((obj, index) => (
                                        <div key={index} className="p-4 border rounded-lg">
                                            <h3 className="font-medium">{obj.name}</h3>
                                            <p className="text-gray-600">{obj.local_term}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500">No objects detected yet. Use the camera to start learning!</p>
                            )}
                        </div>
                    </TabsContent>

                    <TabsContent value="settings" className="flex-1 p-4">
                        <div className="max-w-md mx-auto space-y-6">
                            <div className="bg-white p-6 rounded-lg shadow">
                                <h2 className="text-lg font-medium">Region Settings</h2>
                                <select
                                    value={userRegion}
                                    onChange={(e) => setUserRegion(e.target.value)}
                                    className="mt-2 w-full px-3 py-2 border rounded-lg"
                                >
                                    <option value="Western Cape">Western Cape</option>
                                    <option value="Eastern Cape">Eastern Cape</option>
                                    <option value="KwaZulu-Natal">KwaZulu-Natal</option>
                                    <option value="Free State">Free State</option>
                                </select>
                            </div>

                            <div className="bg-white p-6 rounded-lg shadow">
                                <h2 className="text-lg font-medium">Learning Mode</h2>
                                <div className="mt-4 space-y-4">
                                    <Button
                                        variant={learningMode === 'linguist' ? 'default' : 'outline'}
                                        className="w-full justify-start"
                                        onClick={() => setLearningMode('linguist')}
                                    >
                                        <Globe className="mr-2 h-4 w-4" />
                                        Linguist Mode
                                    </Button>
                                    <Button
                                        variant={learningMode === 'student' ? 'default' : 'outline'}
                                        className="w-full justify-start"
                                        onClick={() => setLearningMode('student')}
                                    >
                                        <Book className="mr-2 h-4 w-4" />
                                        Student Mode
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>
            </main>
        </div>
    );
};

export default LinguaLearnApp;