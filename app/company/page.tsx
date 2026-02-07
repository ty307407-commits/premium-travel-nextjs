import LegalPage, { generateMetadata as generateLegalMetadata } from '@/components/LegalPage';

// Force dynamic rendering
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function generateMetadata() {
    return generateLegalMetadata({ slug: '/company' });
}

export default function CompanyPage() {
    return <LegalPage slug="/company" />;
}
