import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Camera, Book, Settings, Globe } from 'lucide-react';
import ObjectLearningView from './ObjectLearningView';
import ObjectTermList from './ObjectTermList';

export default function LinguaLearnApp() {
    const [activeTab, setActiveTab] = useState('camera');
    const [currentLanguage, setCurrentLanguage] = useState('xho');
    const [userRegion, setUserRegion] = useState('Western Cape');
    const [learningMode, setLearningMode] = useState('linguist'); // 'linguist' or 'student'
    const [terms, setTerms] = useState([]);

    // Initialize object learning system
    useEffect(() => {
        const initializeLearning = async () => {
            try {
                // Load saved terms
                const savedTerms = await window.api.getStoredTerms(currentLanguage);
                setTerms(savedTerms);
            } catch (error) {
                console.error('Failed to initialize:', error);
            }
        };

        initializeLearning();
    }, [currentLanguage]);

    // Handle object capture
    const handleCapture = async (captureData) => {
        try {
            const result = await window.api.detectObject({
                point: captureData.point,
                frame: captureData.frame,
                language: currentLanguage
            });
            return result;
        } catch (error) {
            console.error('Capture failed:', error);
            return { success: false, error: 'Failed to detect object' };
        }
    };

    // Handle term recording
    const handleRecordTerm = async () => {
        try {
            const result = await window.api.recordTerm({
                language: currentLanguage,
                duration: 5 // seconds
            });
            return result;
        } catch (error) {
            console.error('Recording failed:', error);
            return { success: false, error: 'Failed to record term' };
        }
    };

    // Save new term
    const handleSaveTerm = async (termData) => {
        try {
            const result = await window.api.saveTerm({
                ...termData,
                region: userRegion,
                added_by: learningMode === 'linguist' ? 'linguist' : 'student'
            });

            if (result.success) {
                // Update local terms list
                setTerms(prevTerms => [...prevTerms, result.term]);
            }

            return result;
        } catch (error) {
            console.error('Save failed:', error);
            throw error;
        }
    };

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
            <main className="flex-1 overflow-hidden">
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

                    <TabsContent value="camera" className="flex-1 p-4">
                        <ObjectLearningView
                            onCapture={handleCapture}
                            onRecordTerm={handleRecordTerm}
                            onSaveTerm={handleSaveTerm}
                            language={currentLanguage}
                            region={userRegion}
                            learningMode={learningMode}
                        />
                    </TabsContent>

                    <TabsContent value="dictionary" className="flex-1 p-4 overflow-auto">
                        <ObjectTermList
                            terms={terms}
                            onSelectTerm={(term) => {
                                setActiveTab('camera');
                                // TODO: Set up camera to find similar object
                            }}
                            selectedLanguage={currentLanguage}
                            onChangeLanguage={setCurrentLanguage}
                        />
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
}