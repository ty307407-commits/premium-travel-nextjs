import LegalPage, { generateMetadata as generateLegalMetadata } from '@/components/LegalPage';

// Force dynamic rendering
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function generateMetadata() {
    return generateLegalMetadata({ slug: '/privacy' });
}

export default function PrivacyPage() {
    return <LegalPage slug="/privacy" />;
}
